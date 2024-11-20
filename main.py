import requests 
from itertools import count
from dotenv import load_dotenv
import os
from terminaltables import AsciiTable




def predict_rub_salary(salarys_from=None, salarys_to=None):
    if salarys_from and salarys_to:
        expected_salary = (salarys_from+salarys_to)/2
        return expected_salary
    elif salarys_from:
        return salarys_from*1.2
    elif salarys_to:
        return salarys_to*0.8
    else:
        return None


def get_vacancies_by_languages_hh():
    vacancies_by_languages = {

    }
    languages = ["Ruby", "Go"]
    for language in languages:
    
        all_salary = []
        vacancies_processed = 0
        for page in count(0):
            url = "https://api.hh.ru/vacancies"
            payload = {
                "text": language,
                "area": 1,
                "period": 30,
                "page": page
            }
            response = requests.get(url, params=payload)
            response.raise_for_status()
            vacancies = response.json()
            if page >= vacancies['pages']-1:
                break
            for vacancy in vacancies["items"]:
                salarys = vacancy.get('salary') 
                if salarys and salarys["currency"] == "RUR":
                    predicted_salary = predict_rub_salary(vacancy["salary"].get("from"), vacancy["salary"].get("to"))
                    if predicted_salary:
                        all_salary.append(predicted_salary)
                        vacancies_processed += 1
        found_vacancy = response.json()["found"]
        if all_salary:
            average_salary = int(sum(all_salary)/len(all_salary))
        vacancies_by_languages[language] = { 
            "vacancies_found": found_vacancy,
            "vacancies_processed": vacancies_processed,
            "average_salary": average_salary
        }
    return vacancies_by_languages


def predict_rub_salary_for_superJob(sj_key):
    vacancies_by_languages = {}
    languages = ["Python", "Java"]
    for language in languages:
        all_salaries = []
        for page in count(0):
            headers = {
                "X-Api-App-Id": sj_key,
            }
            payload = {
                "keyword": language,
                "town": "Москва",
                "page": page
            }
            url = "	https://api.superjob.ru/2.0/vacancies/"
            response = requests.get(url, headers=headers, params=payload)
            vacancies = response.json()
            response.raise_for_status()
            if not vacancies["objects"]:
                break
            for vacancy in vacancies["objects"]:
                predicted_salary = predict_rub_salary(vacancy.get('payment_from'), vacancy.get('payment_to'))
                if predicted_salary:
                    all_salaries.append(predicted_salary)
            found_vacancy = vacancies["total"]
        if all_salaries:
            average_salary = int(sum(all_salaries)/len(all_salaries))
        else:
            average_salary = None              
        vacancies_by_languages[language] = { 
            "vacancies_found": found_vacancy,
            "vacancies_processed": len(all_salaries),
            "average_salary": average_salary
        }
    return vacancies_by_languages


def get_table(vacancies_by_languages, title):
    table_data = [
            ["Язык программирования", "Вакансий найдено", "Вакансий обработано", "Средняя зарплата"]
        ]
    for laguage, vacancies in vacancies_by_languages.items():
        table_data.append(
            [
                laguage,
                vacancies['vacancies_found'],
                vacancies['vacancies_processed'],
                vacancies['average_salary']
            ]
        )
    table = AsciiTable(table_data, title)           
    return table.table


def main():
    load_dotenv()
    sj_key = os.environ['SUPERJOB_KEY']
    print(get_table(predict_rub_salary_for_superJob(sj_key), "SuperJob Moscow"))
    print(get_table(get_vacancies_by_languages_hh(), "HeadHunter Moscow"))


if __name__ == '__main__':
    main()