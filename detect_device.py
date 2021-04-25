import os

def detect_device():
    ''' Triess to detect which device is running the code. If successful, there is no need to manually set which is the inside and outside deivce.
    NB! Only made with Raspberry Pi models in mind. Any other system will probably have to either modify this code or split the code manually'''

    error_msg = 'Unable to detect rpi type from /sys/firmware/devicetree/base/model. Consider splitting the code manually in the main module'
    try:
        model = os.popen('cat /sys/firmware/devicetree/base/model').read()
    except Exception as e:
        raise e
    inside_models = ['Raspberry Pi 3', 'Raspberry Pi 4', 'Raspberry Pi 2']
    outside_models = ['Zero']
    print(model)
    
    if any([x for x in inside_models if x in model]):
        return 'inside_rpi'
    elif any([x for x in outside_models if x in model]):
        return 'outside_rpi'
    else:
        raise RuntimeError(error_msg) 


if __name__ == '__main__':
    print(detect_device())
