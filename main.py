import requests
from numpy import average
from itertools import count
from terminaltables import AsciiTable
from environs import Env

SEARCH_PERIOD = 30
CITY_CODE = 1
VACANTION_CATEGORY_ID = 48
RESULTS_ON_PAGE = 100

def main():
    
    env = Env()
    env.read_env()
    superJob_security_id = env('SUPERJOB_SECURITY_CODE')

    languages = [
        'Python',
        'Java',
        'С++',
        'TypeScript',
        'Swift',
        'Scala',
        'Objective-C',
        'C#',
        'PHP',
        'Ruby',
    ]
    print(get_hh_salary(languages))
    print(get_superjob_salary(languages, superJob_security_id))


def get_hh_salary(languages):

    url = "https://api.hh.ru/vacancies/"
    header = {'User-Agent': 'Nik_DVMN'}
    hh_salary = {}

    for language in languages:
        avr_salaries = []
        for page in count(0):
            params = {
                "text": f" {language}",
                "area": CITY_CODE,
                "period": SEARCH_PERIOD,
                "page": page,
            }
            response = requests.get(url, headers=header, params=params)
            response.raise_for_status()
            response = response.json()

            for job in response['items']:
                salary = predict_rub_salary_for_hh(job['salary'])
                if salary:
                    avr_salaries.append(salary)
            if page == response['pages']-1:
                vacations_found = response['found']
                break
        hh_salary[language] = { "vacancies_found": vacations_found,
                                "vacancies_processed": len(avr_salaries),
                                "average_salary": int(average(avr_salaries))
                               }
    for_print_salary = prepare_for_print(hh_salary)
    salary_table = AsciiTable(for_print_salary, title='HH Moscow')
    return salary_table.table


def get_superjob_salary(languages, security_id):
    url = "https://api.superjob.ru/2.0/vacancies/"
    header = {
        "X-Api-App-Id": security_id,
    }
    superJob_salary = {}

    for language in languages:
        avr_salaries = []
        for page in count(0):
            params = {
                "keyword": f"{language}",
                "town": "Москва",
                "catalogues": VACANTION_CATEGORY_ID,
                "page": page,
                "count": RESULTS_ON_PAGE,
                }
            response = requests.get(url, headers=header, params=params)
            response.raise_for_status()
            response = response.json()

            if not response["total"]:
                break

            for job in response['objects']:
                salary = calculate_avg_salary(job['payment_from'], job['payment_to'])
                if salary:
                    avr_salaries.append(salary)

            if not response['more']:
                break

        if response["total"]:
            superJob_salary[language] = {"vacancies_found": response["total"],
                                    "vacancies_processed": len(avr_salaries),
                                    "average_salary": int(average(avr_salaries))
                                    }

    for_print_salary = prepare_for_print(superJob_salary)
    salary_table = AsciiTable(for_print_salary, title = 'SuperJob Moscow')
    return salary_table.table


def predict_rub_salary_for_hh(salary_hh):

    if not salary_hh:
        return None

    salary_from = salary_hh['from']
    salary_to = salary_hh['to']
    salary_currency = salary_hh['currency']

    if salary_currency != 'RUR':
        return None
    return calculate_avg_salary(salary_from, salary_to)


def calculate_avg_salary(salary_from, salary_to):
    if not salary_from and not salary_to:
        return None
    elif salary_from and salary_to:
        return (int(salary_from) + int(salary_to)) / 2
    elif not salary_from:
        return int(salary_to) * 0.8
    elif not salary_to:
        return int(salary_from) * 1.2
    

def prepare_for_print(salary_info):

    output_table = [["Язык", "Всего вакансий", "Использовано в расчете", "Средняя зарплата"],]
    for language, jobs  in salary_info.items():
        table_line = [language] + list(jobs.values())
        output_table.append(table_line)
    return output_table


if __name__ == "__main__":
    main()
