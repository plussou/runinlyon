from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.keys import Keys
import geckodriver_autoinstaller
import logging
import pandas as pd
import copy

geckodriver_autoinstaller.install()
options = Options()
options.headless = True


#  Scrapping data from Active Result web site
# --------------------------------------------

def get_full_ranking(url, course, total_number_of_results, logger, debbug=False):
    ''' get the full ranking table for a given course'''

    logger.info('--- start get_full_ranking ---')
    logger.info(f'url    : {url}')
    logger.info(f'course : {course}')
    if debbug :
        total_number_of_results = 5
        logger.info('!! mode test !!')
    logger.info(f'n_bib  : {total_number_of_results}')

    ''' step 1: select course from menu'''

    driver = webdriver.Firefox(options=options)
    driver.get(url)

    entry_found = False
    while not entry_found:
        driver.implicitly_wait(2)
        try:
            entry_found = True
            view_selectors = driver.find_element_by_class_name('dropdown-group')
        except Exception:
            entry_found=False

        drop_down_buttons = view_selectors.find_elements_by_class_name('labeled-dropdown')

    course_menu = 0
    for i in range(len(drop_down_buttons)):
        label = drop_down_buttons[i].find_element_by_class_name('labeled-dropdown__label').text.strip()
        logger.info(f'menu {i}->{label}<-')
        if (label.find('Course') >= 0) or (label.find('Parcours') >= 0):
            label_menu = copy.copy(label)
            course_menu = copy.copy(i)

    button = drop_down_buttons[course_menu].find_element_by_class_name('dropdown__button')
    menu = drop_down_buttons[course_menu].find_element_by_class_name('dropdown__menu')
    menu_items = menu.find_elements_by_tag_name('li')

    course_item = None
    for i, item in enumerate(menu_items):
        label = item.find_element_by_tag_name('a').get_attribute('innerHTML').strip()
        if label==course:
            course_item = copy.copy(i)
    if not isinstance(course_item, int):
        logger.info(f'{course} not found')
        return []

    logger.info(f'From menu       :{label_menu}')
    logger.info(f'Selecting course:{course}')

    driver.execute_script("arguments[0].click();", button)
    driver.execute_script("arguments[0].click();", menu_items[course_item])

    ''' step 3: load results by 50'''
    n_results = len(driver.find_elements_by_class_name('event-home__item'))

    while n_results<total_number_of_results:
        n_reloads = ((total_number_of_results - n_results)//50)+1
        for i in range(n_reloads):
            try:
                driver.implicitly_wait(2)
                view_more_footer = driver.find_element_by_class_name('view-more-list__footer')
                button = view_more_footer.find_element_by_tag_name('a')
                driver.execute_script("arguments[0].click();", button)
            except Exception:
                print('waiting 5 more seconds')
                driver.implicitly_wait(5)
        n_results = len(driver.find_elements_by_class_name('event-home__item'))

    logger.info(f'ready to read {n_results} results')

    '''step 4: read results'''
    data = []
    for element in driver.find_elements_by_class_name('event-home__item'):
        rank = element.find_element_by_class_name('event-home__rank').text
        bib = element.find_element_by_class_name('event-home__bib').find_element_by_class_name('event-home__result').text
        sex,age = element.find_element_by_class_name('event-home__person').find_element_by_class_name('event-home__info').text.split('|')
        time = element.find_element_by_class_name('event-home__finish').find_element_by_class_name('event-home__result').text
        data.append([rank,bib,sex.strip(), int(age.replace('Age','').strip()),time])

    driver.close()
    data_df = pd.DataFrame(data,columns=['rank','bib','sex','age','time'])
    logger.info(f'return {len(data_df)} rows result table')

    return data_df.set_index(keys='rank')


def get_bib_results(driver,bib):
    ''' navigate in the the web site to get results according to bib number
        returns a list with gun_time, 5k_time, 10k_time'''

    results = []

    input_found = False
    while not input_found:
        input_found = True
        try:
            bib_input = driver.find_element_by_class_name('input')
        except:
            input_found = False
            driver.implicitly_wait(5)

    bib_input.send_keys(str(bib))
    bib_input.send_keys(Keys.ENTER)

    participants_found = False
    while not participants_found:
        participants_found = True
        try:
            participants = driver.find_elements_by_class_name("search-participant-list-item")
        except:
            participants_found = False
            driver.implicitly_wait(5)

    if len(participants) >= 1:
        links = participants[0].find_elements_by_tag_name('a')
        driver.execute_script("arguments[0].click();", links[0])
        driver.implicitly_wait(2)

        result_card = driver.find_elements_by_class_name('result-data--data-number')
        result_split = driver.find_elements_by_class_name('result-cell')

        if len(result_card) >= 2:
            gun_time = result_card[1].text
        else:
            gun_time = 0

        results.append(gun_time)

        time_steps = []
        for result in result_split:
            time_label = result.find_element_by_class_name('result-cell-title').text
            if 'Total' in time_label:
                time_steps.append(result.find_element_by_class_name('result-cell-content').text)

        if len(time_steps)>=2:
            results.append(time_steps[0])
            results.append(time_steps[1])

        input_found = False
        while not input_found:
            input_found = True
            try :
                bib_input = driver.find_element_by_class_name('input')
                bib_input.clear()
            except :
                input_found = False
                driver.implicitly_wait(5)

    else:
        input_found = False
        while not input_found:
            input_found = True
            try :
                bib_input = driver.find_element_by_class_name('input')
                bib_input.clear()
            except :
                input_found = False
                driver.implicitly_wait(5)

    return driver, results

def inspect_event():

    logging.basicConfig(filename='runinlyon.log', encoding='utf-8', level=logging.INFO)

    # create logger
    logger = logging.getLogger('runin_run')
    logger.setLevel(logging.DEBUG)

    # create file handler which logs even debug messages
    fh = logging.FileHandler('runnin.log')
    fh.setLevel(logging.DEBUG)

    logger.addHandler(fh)

    event_base = 'RunInLyon2019'
    event_specific = 'Running | Semi-Marathon'
    nb_results = 9498
    url = f'https://resultscui.active.com/events/{event_base}'
    event_df = get_full_ranking(url,event_specific,nb_results,logger,debbug=True)
    print(event_df)
