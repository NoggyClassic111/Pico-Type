from PicoBoySDK import PicoBoySDK
from machine import USBDevice
import time
from micropython import const
PicoBoy=PicoBoySDK(namespace="Pico Type")
# --- 1. Bare-bones descriptors ---------------------------------
usb = USBDevice()
usb.active(False)
desc_dev = bytes((
    18,   const(1),          # bLength, bDescriptorType = DEVICE
    0x00, 0x02,              # bcdUSB = 2.00
    0x00, 0x00, 0x00,        # bDeviceClass/SubClass/Protocol = vendor-specific
    64,                      # bMaxPacketSize0
    0x8A, 0x2E,              # idVendor  = 0x2E8A   << CHANGED
    0x06, 0x00,              # idProduct = 0x0005   << CHANGED
    0x00, 0x01,              # bcdDevice = 1.00
    1, 2, 3,                 # iManufacturer, iProduct, iSerial
    1                        # bNumConfigurations
))

# Config with a single vendor-specific interface, EP1 OUT & EP1 IN
CFG_LEN = 34         # = 32 bytes in your example
desc_report= (
    b'\x05\x01'     # Usage Page (Generic Desktop),
        b'\x09\x06'     # Usage (Keyboard),
    b'\xA1\x01'     # Collection (Application),
        b'\x05\x07'         # Usage Page (Key Codes);
            b'\x19\xE0'         # Usage Minimum (224),
            b'\x29\xE7'         # Usage Maximum (231),
            b'\x15\x00'         # Logical Minimum (0),
            b'\x25\x01'         # Logical Maximum (1),
            b'\x75\x01'         # Report Size (1),
            b'\x95\x08'         # Report Count (8),
            b'\x81\x02'         # Input (Data, Variable, Absolute), ;Modifier byte
            b'\x95\x01'         # Report Count (1),
            b'\x75\x08'         # Report Size (8),
            b'\x81\x01'         # Input (Constant), ;Reserved byte
            b'\x95\x05'         # Report Count (5),
            b'\x75\x01'         # Report Size (1),
        b'\x05\x08'         # Usage Page (Page# for LEDs),
            b'\x19\x01'         # Usage Minimum (1),
            b'\x29\x05'         # Usage Maximum (5),
            b'\x91\x02'         # Output (Data, Variable, Absolute), ;LED report
            b'\x95\x01'         # Report Count (1),
            b'\x75\x03'         # Report Size (3),
            b'\x91\x01'         # Output (Constant), ;LED report padding
            b'\x95\x06'         # Report Count (6),
            b'\x75\x08'         # Report Size (8),
            b'\x15\x00'         # Logical Minimum (0),
            b'\x25\x65'         # Logical Maximum(101),
        b'\x05\x07'         # Usage Page (Key Codes),
            b'\x19\x00'         # Usage Minimum (0),
            b'\x29\x65'         # Usage Maximum (101),
            b'\x81\x00'         # Input (Data, Array), ;Key arrays (6 bytes)
    b'\xC0'     # End Collection
)
desc_cfg = bytes((
    9, 2,  34, 0,   # wTotalLength LSB/MSB
    1, 1, 0, 0xA0, 0x19,                    # 1 interface, 100 mA
    # Interface 0
    9, 4, 0, 0, 1, 0x03, 0x01, 0x01, 0,
    
    #HID Descriptors
    0x09,0x21,0x11,0x01,0x00,0x01,0x22,0x3F,0x00,
    # EP1  IN  bulk
    7, 5, 0x81, 3, 0x08, 0, 0x0A
 
   
))
keyBuffer = (0x00,0x00,0x00,0x00,0x00,0x00)
debounceWait = 1000 #in milliseconds



assert len(desc_cfg) == CFG_LEN
# Strings (index 0 is automatic “English”)
desc_strs = {
    1: "Pico Inc.",
    2: "Keyboard",
    3: "SN12345"
}

# --- 2. (Optional) callback just to echo bulk data --------------
rx_buf = bytearray(8)
#tx_buf = memoryview(rx_buf)  # reuse the same RAM
EP_OUT = 0x01

strexc = []
keyLock = False
def open_itf_cb(itf_desc_view):
    global keyLock
    keyLock = True
    pass
    

def xfer_cb(ep, ok, nbytes):
    #strexc.append(str(ok))
    return True
    pass
def control_xfer_cb(cts,data):
    try:
        
        strexc.append(str(int(data[0])) + " " + str(int(data[1])) + " " + str(int(data[3])) )
        strexc.append("cts: " +str(cts))
        if cts == 1:
       
       
            
    
            
            if int(data[3]) == 34:
                strexc.append("didit")
                return desc_report
            if int(data[0]) == 2:
                strexc.append("didit2")
                return bytes(0)
            strexc.append("didit3")
           
        if(data[1] == 0x09 and cts == 1):
            return bytearray(1)
        elif(data[1] == 0x09):
            return  True
        else:
            return True
    except Exception as e:
        strexc.append(str(e))
   
    pass

# --- 3. Configure & activate ------------------------------------


#usb.active(False)
def configUsb():
    try:
        usb.config(desc_dev, desc_cfg, desc_strs, xfer_cb=xfer_cb,open_itf_cb = open_itf_cb,control_xfer_cb=control_xfer_cb)
    except Exception as e:
        strexc.append(str(e))

def sendKeys(keyBuffer = keyBuffer):

    try:
        if keyLock:
            keysToSend = (0x00,0x00) + keyBuffer
            usb.submit_xfer(0x81,bytearray(keysToSend))
            time.sleep_ms(30)
        #usb.submit_xfer(0x81,bytearray((0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00)))
    except Exception as e:
        return None

def insertKeyInToBuffer(keyCode,localKeyBuffer):
    keyBufferAsArray = [x for x in localKeyBuffer]
    for i in range(0,len(localKeyBuffer)):
        if localKeyBuffer[i] == 0x00:
            keyBufferAsArray[i] = keyCode
            break
    return tuple(keyBufferAsArray)
        



# trigs re-enumeration

# Queue the first OUT transfer so the host can send data

def callBackTest(key,holding,inputVal):
    
        print(key)
        global keyBuffer
        keyBuffer = insertKeyInToBuffer(inputVal["keycode"],keyBuffer)
       
    
inputs = {
    "Default": { "callback":callBackTest},

    # action buttons
    "A":        {"keycode": 0x2A},      # Enter
    "B":        {"keycode": 0x2A},      # Backspace

    # d-pad (arrow keys)
    "Up":       {"keycode": 0x52},      # ↑
    "Down":     {"keycode": 0x51},      # ↓
    "Left":     {"keycode": 0x50},      # ←
    "Right":    {"keycode": 0x4F},      # →

    # system buttons
    "Start":    {"keycode": 0x29},      # Escape
    "Select":   {"keycode": 0x2B}       # Tab
}
def checkInput(inputKey,inputVal,inputs = inputs):
    isPressed = PicoBoy.Button(inputKey)
    debounce = inputVal.get("debounce",True)
    holding = isPressed and not debounce
    callback = inputVal.get("callback",None) or inputs["Default"].get("callback",None)
    
    if isPressed and callback:
        callback(inputKey, holding,inputVal)
        
    inputVal["debounce"] = not isPressed
    
    return inputVal
    
    
def checkInputs(inputs = inputs):
    for key, val in inputs.items():
        inputs[key] = checkInput(key,val)
def cleanup():
    try:
       
        global keyBuffer
        tempKeyBuffer = (0x00,0x00,0x00,0x00,0x00,0x00)
        if keyBuffer != tempKeyBuffer:
            sendKeys(keyBuffer)
            keyBuffer = tempKeyBuffer
            #sendKeys(keyBuffer)
        else:
            sendKeys(tempKeyBuffer)
            
        
        
       
        
    except Exception as e:
        strexc = [str(e)]
        PicoBoy.Update()
        print(e)
        
    
          
def checkUSB():
    try:
        if not usb.active():
            global keyLock
            keyLock = False
            usb.active(True)
        else:
            pass
            
    except Exception as e:
        pass
    
    

configUsb()

while True:
    
    try:
        checkInputs()
        checkUSB()
        PicoBoy.Render_Popup((192,192,192),(0,0,0),0,0,150,"Key Legend",[
    "A - Enter",
    "B - Backspace",
    "Up - Up Arrow",
    "Down - Down Arrow",
    "Left - Left Arrow",
    "Right - Right Arrow",
    "Start - Escape",
    "Select - Tab"
])
    #Put the code you want here, anything graphical must come before PicoBoy.Update()
      
   
        PicoBoy.Update()
        cleanup()
    except Exception as e:
        strexc.append(str(e))




