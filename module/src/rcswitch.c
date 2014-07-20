/*
 * Linux Kernel module for controlling a RCSwitch.
 *
 * Author:
 * 	Stefan Wendler (devnull@kaltpost.de)
 * 
 * Credits: 
 *
 * Most of the parts for sending command to the RCSwitches over RF are
 * taken from xkonis raspbarry-remote: 
 *	https://github.com/xkonni/raspberry-remote
 *
 * This software is licensed under the terms of the GNU General Public
 * License version 2, as published by the Free Software Foundation, and
 * may be copied, distributed, and modified under those terms.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 */

#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/gpio.h>
#include <linux/delay.h>

/* TX-GPIO to 433Mhz sender */
static int tx_gpio = 9;

/* EN-GPIO to 433Mhz sender */
static int en_gpio = 7;

/* duration of a single pulse in usec */
static int pulse_duration = 350;

/* Module param for TX-GPIO */
module_param(tx_gpio, int, 0);
MODULE_PARM_DESC(tx_gpio, "Number of GPIO to which TX of 433Mhz sender is connected (default 9/CTS).");

/* Module param for EN-GPIO */
module_param(en_gpio, int, 0);
MODULE_PARM_DESC(en_gpio, "Number of GPIO to which 3v3 of 433Mhz sender is connected (default 7/RTS).");

/* Module param for pulse duration */
module_param(pulse_duration, int, 0);
MODULE_PARM_DESC(pulse_duration, "Duration of a single pulse in usec. (default 350)");

void send(const char *command);

/**
 * SYSFS STUFF (to register controll interface under /sys/kernel/rcswitch/comman
 */

/*
 * send command to switch
 */
static ssize_t sysfs_command_store(struct kobject *kobj, struct kobj_attribute *attr, const char *buf, size_t count)
{
    send(buf);

    return count;
}

static struct kobj_attribute command_attribute = __ATTR(command, 0222, NULL, sysfs_command_store);

/* List of all attributes exported to sysfs */
static struct attribute *attrs[] = {
    &command_attribute.attr,
    NULL,
};

/* Attributes for sysfs in a group */
static struct attribute_group attr_group = {
    .attrs = attrs,
};


/* Kernel object for sysfs */
static struct kobject *rcswitch_kobj;

/**
 * Sends a Tri-State "0" Bit
 *            _     _
 * Waveform: | |___| |___
 */
#define SEND_T0()	transmit(1,3); transmit(1,3)

/**
 * Sends a Tri-State "1" Bit
 *            ___   ___
 * Waveform: |   |_|   |_
 */
#define SEND_T1() 	transmit(3,1); transmit(3,1)

/**
 * Sends a Tri-State "F" Bit
 *            _     ___
 * Waveform: | |___|   |_
 */
#define SEND_TF() 	transmit(1,3); transmit(3,1)

/**
 * Sends a "Sync" Bit
 *                       _
 * Waveform Protocol 1: | |_______________________________
 *                       _
 * Waveform Protocol 2: | |__________
 */
#define SEND_SYNC() 	transmit(1,31)

/**
 * Make code-word
 */
char *get_code_word(char* group, int channel_code, int status)
{
    int i = 0;
    int ret_pos = 0;
    static char ret[13];

    char* code[6] = { "FFFFF", "0FFFF", "F0FFF", "FF0FF", "FFF0F", "FFFF0" };

    if (channel_code < 1 || channel_code > 5) 
    {
        return 0;
    }

    for (i = 0; i<5; i++)
    {
        if (group[i] == '0')
        {
            ret[ret_pos++] = 'F';
        }
        else if (group[i] == '1')
        {
            ret[ret_pos++] = '0';
        }
        else
        {
            return 0;
        }
    }

    for (i = 0; i<5; i++)
    {
        ret[ret_pos++] = code[ channel_code ][i];
    }

    if (status)
    {
        ret[ret_pos++] = '0';
        ret[ret_pos++] = 'F';
    }
    else
    {
        ret[ret_pos++] = 'F';
        ret[ret_pos++] = '0';
    }

    ret[ret_pos] = 0;

    return ret;
}


/**
 * Transmit high low/pulse
 */
void transmit(int high_count, int low_count)
{
    gpio_set_value(tx_gpio, 1);
    udelay(pulse_duration * high_count);
    gpio_set_value(tx_gpio, 0);
    udelay(pulse_duration * low_count);
}

/**
 * Sends a code word
 */
void send_tri_state(char* code_word)
{
    int repeat = 0;
    int i = 0;

    for(repeat=0; repeat<10; repeat++)
    {
        i = 0;
        while (code_word[i] != 0)
        {
            switch(code_word[i])
            {
            case '0':
                SEND_T0();
                break;
            case 'F':
                SEND_TF();
                break;
            case '1':
                SEND_T1();
                break;
            }
            i++;
        }
        SEND_SYNC();
    }
}

/**
 * Send string command to switch.
 * 
 * Format is: 
 * 
 * AAAAACS
 * 
 * Where: 
 * AAAAA 	- address bits - e.g. '11111'
 * C		- channel A, B, C or D - e.g. 'A'
 * S		- state 1 (on) or 0 (off) - e.g. '1'
 * 
 * Complete command string examples: 
 *  
 * '11111A0' 	- Switch channel A off for address '11111' 
 * '11111B1' 	- Switch channel B on  for address '11111' 
 */
void send(const char *command)
{
    static char  address[] = {0, 0, 0, 0, 0, 0};
    int   channel = 0;
    int   state   = 0;
    int   i       = 0;

    if(strlen(command) < 7)
    {
        printk("Command lenght MUST be at least 7 characters\n");
        return;
    }

    /* copy address part */
    for(i = 0; i < 5; i++)
    {
        if(command[i] == '0' ||  command[i] == '1')
        {
            address[i] = command[i];
            // printk("address[%d] = command[%d] = %c\n", i, i, command[i]);
        }
        else
        {
            printk("Invalid character in address part (only 0 and 1 allowed, but found %c)\n", command[i]);
            return;
        }
    }

    /* copy channel part */
    if(command[i] >= 'A' && command[i] <= 'D')
    {
        channel = command[i++] - 'A' + 1;
    }
    else
    {
        printk("Invalid character in channel part (only A, B, C and D allowed, but found %c)\n", command[i]);
        return;
    }


    /* copy state part */
    if(command[i] == '0' || command[i] == '1')
    {
        state = command[i] - '0';
    }
    else
    {
        printk("Invalid character in state part (only 0 and 1 allowed, but found %c)\n", command[i]);
        return;
    }

    // printk("Sending: address=%s, channel=%d, state=%d\n", address, channel, state);

    /* send it */
    send_tri_state(get_code_word(address, channel, state));
}

/*
 * Module init function
 */
static int __init rcswitch_init(void)
{
    int ret = 0;

    printk(KERN_INFO "rcswitch: init");
    printk(KERN_INFO "rcswitch: using gpio #%d for TX\n", tx_gpio);
    printk(KERN_INFO "rcswitch: using gpio #%d for EN\n", en_gpio);

    /* register sysfs entry */
    rcswitch_kobj = kobject_create_and_add("rcswitch", kernel_kobj);

    if(!rcswitch_kobj)
    {
        return -ENOMEM;
    }

    ret = sysfs_create_group(rcswitch_kobj, &attr_group);

    if(ret)
    {
        kobject_put(rcswitch_kobj);
        return ret;
    }

    printk(KERN_INFO "rcswitch: registered command interface under: /sys/kernel/rcswitch/command\n");

    /* register TX-GPIO */
    ret = gpio_request_one(tx_gpio, GPIOF_OUT_INIT_LOW, "rcswitch_tx");

    if(ret)
    {
        printk(KERN_ERR "Unable to request GPIO for TX: %d\n", ret);
        return ret;
    }

    /* register EN-GPIO */
    ret = gpio_request_one(en_gpio, GPIOF_OUT_INIT_HIGH, "rcswitch_en");

    if(ret)
    {
        gpio_free(tx_gpio);

        printk(KERN_ERR "Unable to request GPIO for EN: %d\n", ret);
        return ret;
    }

    // send("11111A1");

    return ret;
}

/*
 * Module exit function
 */
static void __exit rcswitch_exit(void)
{
    printk(KERN_INFO "rcswitch: exit\n");

    /* remove kobj */
    kobject_put(rcswitch_kobj);


    /* set to low */
    gpio_set_value(tx_gpio, 0);
    gpio_set_value(en_gpio, 0);

    /* unregister */
    gpio_free(tx_gpio);
    gpio_free(en_gpio);
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("Stefan Wendler");
MODULE_DESCRIPTION("Controll RCSwitch");

module_init(rcswitch_init);
module_exit(rcswitch_exit);
