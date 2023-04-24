import os, time, cv2, numpy as np, requests, json

with open('configuration.json') as config:
    config = json.load(config)

    port = str(config['port'])

    notifications = bool(config['notifications'])
    if notifications:
        webhook = str(config['webhook'])
        check_webhook = requests.get(webhook)
        if check_webhook.status_code != 200:
            print('> Invalid webhook')

            notifications = False

    custom_coordinates = bool(config['custom_coordinates'])
    if custom_coordinates:
        with open('city_layout.json') as layout:
            layout = json.load(layout)

        scout_camp_x, scout_camp_y, scout_camp_ui_x, scout_camp_ui_y = str(layout['scout_camp_x']), str(layout['scout_camp_y']), str(layout['scout_camp_ui_x']), str(layout['scout_camp_ui_y'])

    else:
        scout_camp_x, scout_camp_y, scout_camp_ui_x, scout_camp_ui_y = 963, 477, 81, 816

ip = '127.0.0.1'
emulator = str(f'{ip}:{port}')

map_path = 'images/map.jpg'
home_path = 'images/home.jpg'

screenshot_path = 'images/screenshot.png'

both_scouts_out_path = 'images/scouts/both_out.jpg'
both_scouts_available_path = 'images/scouts/both_available.jpg'

purple_available_path = 'images/scouts/purple_available.jpg'
blue_available_path = 'images/scouts/blue_available.jpg'

explore_button_path = 'images/explore_button.jpg'
explore_fog_button_path = 'images/explore_fog_button.jpg'
in_menu_path = 'images/in_menu.jpg'
send_scout_button_path = 'images/send_scout_button.jpg'

verification_menu_path = 'images/verification_menu.png'
verification_notification_path = 'images/verification_notification.png'

barb_level_6 = 'images/barb_levels/barb_level_6.jpg'

find_image_threshold = 0.5

check_devices = os.system('adb devices > NUL')

if str(emulator) not in str(check_devices):
    os.system(f'adb connect {emulator} > NUL')

def clear():
    kernel = os.name
    match kernel:
        case 'nt':
            os.system('cls')

        case _:
            os.system('clear')

def click_position(x, y):
    os.system(f'adb shell input touchscreen tap {x} {y} > NUL')

def pull_image():
    os.system('adb pull /sdcard/screenshot.png > NUL')
    os.system('move screenshot.png images > NUL')

def screenshot():
    os.system('adb shell screencap -p /sdcard/screenshot.png > NUL')

def get_location(image, image_to_look_for, threshold):
    image1 = cv2.imread(image)
    image2 = cv2.imread(image_to_look_for)

    image1_gray = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    image2_gray = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    result = cv2.matchTemplate(image1_gray, image2_gray, cv2.TM_CCOEFF_NORMED)

    locations = cv2.findNonZero((result > threshold).astype(np.uint8))

    if locations is not None:
        locations = locations.astype(np.int32)
        (x, y, w, h) = cv2.boundingRect(locations.squeeze())
        return (x, y)
    else:
        return None

def find_image(image, image_to_look_for, threshold):
    image1 = cv2.imread(image)
    image2 = cv2.imread(image_to_look_for)
    result = cv2.matchTemplate(image1, image2, cv2.TM_CCOEFF_NORMED)
    if cv2.minMaxLoc(result)[1] >= threshold:
        return True
    else:
        return False

def delete_screenshot():
    if os.path.exists('images/screenshot.png'):
        os.remove('images/screenshot.png')

def screenshot_pull():
    screenshot()
    pull_image()

def new_frame():
    delete_screenshot()
    screenshot()
    pull_image()

def automatic_scout():
    try:
        while True:
            new_frame()
            time.sleep(0.3)
            if get_location(image=screenshot_path, image_to_look_for=in_menu_path, threshold=0.8) is not None:
                print('> Exiting menu')
                click_position(x=1366, y=103)

            for i in range(2):
                new_frame()
                if get_location(image=screenshot_path, image_to_look_for=verification_notification_path, threshold=0.8) is not None:
                    if notifications:
                        with open(screenshot_path, "rb") as data:
                            file_data = data.read()
                        requests.post(webhook, data={'content': '@everyone captcha detected wakey wakey cunt'}, files={"file": ("screenshot.png", file_data)})

                    input('> Captcha detected, please fill it out, then press enter: ')
                    break

            for i in range(2):
                new_frame()
                if get_location(image=screenshot_path, image_to_look_for=verification_menu_path, threshold=0.8) is not None:
                    if notifications:
                        with open(screenshot_path, "rb") as data:
                            file_data = data.read()
                        requests.post(webhook, data={'content': '@everyone captcha detected wakey wakey cunt'}, files={"file": ("screenshot.png", file_data)})

                    input('> Captcha detected, please fill it out, then press enter: ')
                    break

            time.sleep(0.5)
            new_frame()
            
            if get_location(image=screenshot_path, image_to_look_for=home_path, threshold=0.8) is not None:
                print('> Returning home')
                click_position(x=81, y=816)
                
            time.sleep(1.5)
            click_position(x=scout_camp_x, y=scout_camp_y)
            print('> Clicked scout camp')

            time.sleep(0.5)
            click_position(x=scout_camp_ui_x, y=scout_camp_ui_y)
            print('> Clicked scout camp ui')
            
            while True:
                new_frame()
                time.sleep(0.2)
                coordinates_scouts = get_location(image=screenshot_path, image_to_look_for=explore_button_path, threshold=0.7)
                if coordinates_scouts is not None:
                    break
            
            click_position(x=coordinates_scouts[0], y=coordinates_scouts[1])
            print(f'> Clicked a scout')

            while True:
                new_frame()
                time.sleep(0.5)
                coordinates_scouts = get_location(image=screenshot_path, image_to_look_for=explore_fog_button_path, threshold=0.7)
                if coordinates_scouts is not None:
                    break

            time.sleep(0.2)
            click_position(x=coordinates_scouts[0], y=coordinates_scouts[1])
            print(f'> Clicked explore button')
            
            while True:
                new_frame()
                time.sleep(0.5)
                coordinates_scouts = get_location(image=screenshot_path, image_to_look_for=send_scout_button_path, threshold=0.7)
                if coordinates_scouts is not None:
                    break

            click_position(x=coordinates_scouts[0], y=coordinates_scouts[1])
            print(f'> Sent scout')
            print('> Looping')
            continue
    
    except KeyboardInterrupt:
        rokbot()

def barb_chaining():
    while True:
        new_frame()
        time.sleep(0.3)
        coordinates_scouts = get_location(image=screenshot_path, image_to_look_for=barb_level_6, threshold=0.7)
        if coordinates_scouts is not None:
            break
    
    print(f'X: {coordinates_scouts[0]} Y: {coordinates_scouts[1]}')


def frame_generator():
    iteration = 0
    while True:
        input('Press enter to screenshot > ')
        os.system(f'adb shell screencap -p /sdcard/screenshot{iteration}.png > NUL')

        os.system(f'adb pull /sdcard/screenshot{iteration}.png > NUL')
        os.system(f'move screenshot{iteration}.png images/frame_generator > NUL')
        iteration +=1
        time.sleep(0.3)

def rokbot():
    print('1 => Scoutbot\n2 => Screenshot Screen\n3 => Barb Chaining')
    script_choice = str(input('> '))
    match script_choice:
        case '1':
            automatic_scout()

        case '2':
            screenshot_pull()
            print('> Screenshot should be located in images/screenshot.png')

        case '3':
            print('> In production')

        case _:
            print('> Invalid script, press enter to return: ')
            rokbot()

rokbot()