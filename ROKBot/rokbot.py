import os, time, cv2, numpy as np

ip = '127.0.0.1'
port = '5855'
emulator = str(f'{ip}:{port}')

map_path = 'images/map.jpg'
home_path = 'images/home.jpg'

screenshot_path = 'images/screenshot.png'

both_scouts_out_path = 'images/scouts/both_out.jpg'
both_scouts_available_path = 'images/scouts/both_available.jpg'

purple_available_path = 'images/scouts/purple_available.jpg'
blue_available_path = 'images/scouts/blue_available.jpg'

explore_button_path = 'images/explore_button.jpg'
in_menu_path = 'images/in_menu.jpg'

find_image_threshold = 0.6

check_devices = os.system('adb devices > NUL')

if str(emulator) not in str(check_devices):
    os.system(f'adb connect {emulator} > NUL')


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
    if os.path.exists(os.path.join('images', 'screenshot.png')):
        os.remove(os.path.join('images', 'screenshot.png'))

def screenshot_pull():
    screenshot()
    pull_image()

def send_scouts(x, y):

    click_position(x=x, y=y)
    time.sleep(1.2)

    new_frame()
    time.sleep(0.5)
    coordinates = get_location(image=screenshot_path, image_to_look_for=explore_button_path, threshold=0.8)

    if coordinates is not None:
        print('> Found explore button')
        click_position(x=coordinates[0], y=coordinates[1])
        print(f'> Clicked coordinates X: {coordinates[0]} Y: {coordinates[1]}')


def check_scouts(scout_camp_image):
    if find_image(image=scout_camp_image, image_to_look_for=both_scouts_out_path, threshold=find_image_threshold):
        print('> No scout available')
        return str('none')

    if find_image(image=scout_camp_image, image_to_look_for=both_scouts_available_path, threshold=find_image_threshold):
        print('> Both scouts available')
        return str('both')

    if find_image(image=scout_camp_image, image_to_look_for=purple_available_path, threshold=find_image_threshold):
        print('> Purple scout available')
        return str('purple')

    if find_image(image=scout_camp_image, image_to_look_for=blue_available_path, threshold=find_image_threshold):
        print('> Blue scout available')
        return str('blue')
    
    else:
        return str('Something has fucked up')

def new_frame():
    delete_screenshot()

    screenshot()
    pull_image()

def go_home():
    if find_image(image=screenshot_path, image_to_look_for=home_path, threshold=0.8):
        return True

    else:
        return False

def go_outside():
    if find_image(image=screenshot_path, image_to_look_for=map_path, threshold=0.8):
        return True
    
    else:
        return False

def get_scout_camp():
    time.sleep(1)
    click_position(x=963, y=477)
    print('> Clicked scout camp')
    time.sleep(1)
    click_position(x=1146, y=669)
    print('> Clicked scout camp ui')

def check_for_menu():
    if find_image(image=screenshot_path, image_to_look_for=in_menu_path, threshold=0.8):
        return True
    
    else:
        return False

def main():
    while True:
        new_frame()
        if check_for_menu():
            click_position(x=1366, y=103)

        time.sleep(1)
        new_frame()
        
        if go_home():
            click_position(x=81, y=816)

        else:
            if not go_outside():
                click_position(x=81, y=816)
            
        time.sleep(1)
        get_scout_camp()
        time.sleep(1)
        new_frame()
        scout_availability = check_scouts(scout_camp_image=screenshot_path)

        if 'purple' in scout_availability:
            send_scouts(x=1251, y=393)
            time.sleep(1.5)
            click_position(x=1518, y=109)
            time.sleep(1)
            click_position(x=1260, y=207)
            continue

        if 'blue' in scout_availability:
            send_scouts(x=1251, y=565)
            time.sleep(1.5)
            click_position(x=1518, y=262)
            time.sleep(1)
            click_position(x=1260, y=360)
            continue

        if 'both' in scout_availability:
            send_scouts(x=1251, y=393)
            time.sleep(1.5)
            click_position(x=1518, y=109)
            time.sleep(1)
            click_position(x=1260, y=207)
            continue

        if 'none' in scout_availability:
            continue

        else:
            print(scout_availability)

main()