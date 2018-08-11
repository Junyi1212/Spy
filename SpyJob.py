# -*- coding: utf8 -*-
from bs4 import BeautifulSoup
import requests
import csv
import time
#import chardet

prefixUrl_1 = "https://search.51job.com/list/080200,000000,0000,00,9,08,%25E5%25B5%258C%25E5%2585%25A5%25E5%25BC%258F%25E8%25BD%25AF%25E4%25BB%25B6,2,"
suffixUrl_1 = ".html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&\
            lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=21&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="

prefixUrl_2 = "https://search.51job.com/list/080200,000000,0000,00,9,08,%25E6%25B5%258B%25E8%25AF%2595%25E5%25B7%25A5%25E7%25A8%258B%25E5%25B8%2588,2,"
suffixUrl_2 = ".html?lang=c&stype=1&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&\
            lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=21&dibiaoid=0&address=&line=&specialarea=00&from=&welfare="

jobKey = ""
jobDict = {
    "EmbededSW":(prefixUrl_1, suffixUrl_1),
    "Tester":(prefixUrl_2, suffixUrl_2)
}

def getJobGps(job_link):
    response = requests.get(job_link, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
    html = BeautifulSoup(response.text, features="html.parser")
    #BeautifulSoup(response.content, features="html.parser", from_encoding="UTF-8")
    try:
        job_gps = html.find_all("div", class_="bmsg inbox")[0].select("p")[0].get_text()[6:]
    except Exception:
        print(job_link)
        job_gps = None
    return job_gps

def getJobPage(csv_writer):
    page = 0
    writeCount = 0
    while True:
        print("="*200)
        page += 1
        #curUrl = prefixUrl+ "%d" % page + suffixUrl
        curUrl = jobDict[jobKey][0] + "%d" % page + jobDict[jobKey][1]
        print("Fetch: ", curUrl)
        response = requests.get(curUrl, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'})
        print(response.status_code)

        html = BeautifulSoup(response.content, features="html.parser", from_encoding="UTF-8")
        # 获取class=dw_table的元素下的所有el元素
        job_list = html.select(".dw_table > .el")

        # 循环在读不到新的job时结束
        if len(job_list) == 1:
            #only el title
            print("No More Page")
            break

        jobCount = 0
        for job in job_list:
            jobCount = jobCount + 1
            if jobCount == 1:
                print("ignore the first item: el title")
                continue

            jobTitle = job.select(".t1")[0].select("span")[0].select("a")[0]["title"]
            jobCompany = job.select(".t2 > a")[0]["title"]
            jobPlace = job.select(".t3")[0].get_text()
            if "异地" in jobPlace:
                #print("异地招聘,过滤......")
                continue

            jobMoney = job.select(".t4")[0].get_text()
            jobDate = job.select(".t5")[0].get_text()
            jobLink = job.select(".t1")[0].select("span")[0].select("a")[0]["href"]
            jobGps = getJobGps(jobLink)

            writeCount = writeCount+1
            print(writeCount, jobTitle, jobCompany, jobPlace, jobMoney, jobDate, jobGps, jobLink)
            csv_writer.writerow([jobTitle, jobCompany, jobPlace, jobMoney, jobDate, jobGps, jobLink])
    print("Get Page End")


if __name__ == "__main__":
    #jobKey = "EmbededSW"
    jobKey = "Tester"
    csv_file = open(jobKey+".csv", "w", -1, "UTF-8")
    csv_writer = csv.writer(csv_file, delimiter=',')
    getJobPage(csv_writer)

    csv_file.close()
    print("End")