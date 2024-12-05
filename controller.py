
import pyfirmata

comport='COM3'

board=pyfirmata.Arduino(comport)


led_1=board.get_pin('d:12:o')
led_2=board.get_pin('d:11:o')
led_3=board.get_pin('d:10:o')
led_4=board.get_pin('d:9:o')
led_5=board.get_pin('d:8:o')
lis = [led_1, led_2, led_3, led_4, led_5]

def led(fingers_up, type):
    if type == 1:
        for res, l in zip(lis, fingers_up):
            res.write(l)
    elif type == 2:
        count = 0
        for i in fingers_up:
            if i == 1:
                count = count + 1
        print(count)
        if count == 1:
            led_1.write(1)
            led_2.write(0)
            led_3.write(0)
            led_4.write(0)
            led_5.write(0)
        elif count == 2:
            led_2.write(1)
            led_1.write(0)
            led_3.write(0)
            led_4.write(0)
            led_5.write(0)
        elif count == 3:
            led_3.write(1)
            led_1.write(0)
            led_2.write(0)
            led_4.write(0)
            led_5.write(0)
        elif count == 4:
            led_4.write(1)
            led_1.write(0)
            led_2.write(0)
            led_3.write(0)
            led_5.write(0)
        elif count == 5:
            led_5.write(1)
            led_1.write(0)
            led_2.write(0)
            led_3.write(0)
            led_4.write(0)
        else:
            led_1.write(0)
            led_2.write(0)
            led_3.write(0)
            led_4.write(0)
            led_5.write(0)