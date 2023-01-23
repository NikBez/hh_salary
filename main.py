import requests
from numpy import average
from itertools import count
from terminaltables import AsciiTable
from environs import Env

env = Env()
env.read_env()


def main():
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

    get_hh_salary(languages)
    get_superjob_salary(languages)



def get_hh_salary(languages):

    url = "https://api.hh.ru/vacancies/"
    header = {'User-Agent': 'Nik_DVMN'}
    hh_salary_info = {}

    for language in languages:
        avr_salaries = []
        for page in count(0):
            params = {
                "text": f" Программист {language}",
                "area": 1,
                "period": 30,
                "page": page,
            }
            response = requests.get(url, headers=header, params=params)
            response.raise_for_status()
            response_json = response.json()

            for vacantion in response_json['items']:
                salary = predict_rub_salary_for_hh(vacantion['salary'])
                if salary:
                    avr_salaries.append(salary)
            if page == response_json['pages']-1:
                vacations_found = response_json['found']
                break
        hh_salary_info[language] = {"vacancies_found": vacations_found,
                                    "vacancies_processed": len(avr_salaries),
                                    "average_salary": int(average(avr_salaries))
                                    }
    forPrint_salary_info = prepare_info_for_print_table(hh_salary_info)
    salary_table = AsciiTable(forPrint_salary_info, title='HH Moscow')
    print(salary_table.table)


def get_superjob_salary(languages):
    url = "https://api.superjob.ru/2.0/vacancies/"
    header = {
        "X-Api-App-Id": env('SUPERJOB_SECURITY_CODE'),
    }
    salary_info = {}

    for language in languages:
        avr_salaries = []
        for page in count(0):
            params = {
                "keyword": f"{language}",
                "town": "Москва",
                "catalogues": 48,
                "page": page,
                "count": 100,
                }
            response = requests.get(url, headers=header, params=params)
            response.raise_for_status()
            response_json = response.json()

            if response_json["total"] == 0:
                break

            for vacantion in response_json['objects']:
                salary = predict_rub_salary_for_superjob(vacantion['payment_from'], vacantion['payment_to'])
                if salary:
                    avr_salaries.append(salary)

            if not response_json['more']:
                break

        if not response_json["total"] == 0:
            salary_info[language] = {"vacancies_found": response_json["total"],
                                    "vacancies_processed": len(avr_salaries),
                                    "average_salary": int(average(avr_salaries))
                                    }

    forPrint_salary_info = prepare_info_for_print_table(salary_info)
    salary_table = AsciiTable(forPrint_salary_info, title = 'SuperJob Moscow')
    print(salary_table.table)


def predict_rub_salary_for_hh(salary_info_from_hh):

    if salary_info_from_hh == None:
        return None

    salary_from = salary_info_from_hh['from']
    salary_to = salary_info_from_hh['to']
    salary_currency = salary_info_from_hh['currency']

    if salary_currency != 'RUR':
        return None
    elif salary_from and salary_to:
        return (int(salary_from) + int(salary_to))/2
    elif not salary_from:
        return int(salary_to)*0.8
    else:
        return int(salary_from)*1.2

def predict_rub_salary_for_superjob(salary_from, salary_to):
    if salary_from == 0 and salary_to == 0:
        return None
    elif salary_from != 0 and salary_to != 0:
        return (int(salary_from) + int(salary_to)) / 2
    elif salary_from == 0:
        return int(salary_to) * 0.8
    elif salary_to == 0:
        return int(salary_from) * 1.2


def prepare_info_for_print_table(salary_info):

    outputTable = [["Язык", "Всего вакансий", "Использовано в расчете", "Средняя зарплата"],]
    for language, vacantions  in salary_info.items():
        tableLine = [language] + list(vacantions.values())
        outputTable.append(tableLine)
    return outputTable


if __name__ == "__main__":
    main()
