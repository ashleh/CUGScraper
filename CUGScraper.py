import os
import requests
from bs4 import BeautifulSoup
import pandas as pd

PATH = os.path.dirname(os.path.realpath(__file__)) + '\\'
BASE_URL = 'http://www.thecompleteuniversityguide.co.uk/league-tables/rankings'


def cookSoup(url):
	with requests.Session() as s:
		r = s.get(url)
		soup = BeautifulSoup(r.text, 'html.parser')

	return soup


def getLinks():
	list_of_links = [BASE_URL]
	soup = cookSoup(BASE_URL)

	for link in soup.find('ul', {'class': 'links'}).findAll('a', href=True):
		list_of_links.append(BASE_URL + link['href'])

	return list_of_links


def getTitle(soup, link):
	if link == BASE_URL:
		title = 'Whole Institution'
	else:
		title = soup.find('h2').contents[0]
		title = " ".join(title.split())

	return title


def getHeader(soup):
	headers = []
	table = soup.find('table', {'class': 'leagueTable hoverHighlight narrow'})

	for item in table.findAll('th'):
				for link in item.findAll('a', text=True):
					link = link.contents[0].strip()
					if 'Click' not in link and '2016' not in link:
						headers.append(link)

	headers.insert(1, 'Last Year')

	return headers


def getRows(soup):
	rows = []
	table = soup.find('table', {'class': 'leagueTable hoverHighlight narrow'})

	for row in table.findAll('tr'):
		cols = row.find_all('td')
		cols = [ele.text.strip() for ele in cols if ele.get('class', "") not in [['quintile', 'detailColumn'], ['quintile', 'highlight']]]
		rows.append(cols)

	return rows


def normaliseData(title, header, rows):
	df = pd.DataFrame(rows, columns=header)
	header_id = header.pop(2)

	normalised_data = pd.melt(df, id_vars=header_id, value_vars=header, var_name='Measure', value_name='Value')
	normalised_data.insert(0, 'Subject', title)
	normalised_data = normalised_data.dropna(subset=['University Name'], how='all')

	return normalised_data


def combineData(link):
	soup = cookSoup(link)
	title = getTitle(soup, link)
	header = getHeader(soup)
	rows = getRows(soup)
	combined_data = normaliseData(title, header, rows)

	return combined_data


def main():
	joined_subjects = []
	list_of_links = getLinks()
	for link in list_of_links:
		joined_subjects.append(combineData(link))

	pd.concat(joined_subjects).to_csv(PATH + 'final.csv', sep=',', index=False)


if __name__ == "__main__":
	main()
