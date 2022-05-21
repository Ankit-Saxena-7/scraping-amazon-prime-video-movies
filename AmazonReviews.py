# Source: https://www.youtube.com/watch?v=DIT8rwyPEns&ab_channel=JohnWatsonRooney
# https://dataminer.io/
# Replace / with - in movie names

import requests
from bs4 import BeautifulSoup
import pandas as pd
import os.path

def get_soup(url):
    r = requests.get('http://localhost:2012/render.html', params={'url': url, 'wait': 2})
    soup = BeautifulSoup(r.text, 'html.parser')
    return soup


def get_reviews_unhelpful(soup, reviewlist):
    reviews = soup.find_all('div', {'data-hook': 'review'})
    try:
        for item in reviews:

            date = item.find('span', {'data-hook': 'review-date'}).text.strip() or '',
            title = item.find('a', {'data-hook': 'review-title'}).text.strip() or '',
            rating = float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()) or None,
            body = item.find('span', {'data-hook': 'review-body'}).text.strip() or ''
            #helpful = item.find('span', {'data-hook': 'helpful-vote-statement'}).text.strip() or ''

            review = {'date': date, 'title': title, 'rating': rating, 'body': body}

            reviewlist.append(review)
    except:
        pass

def get_reviews_helpful(soup, reviewlist):
    reviews = soup.find_all('div', {'data-hook': 'review'})
    try:
        for item in reviews:

            date = item.find('span', {'data-hook': 'review-date'}).text.strip() or '',
            title = item.find('a', {'data-hook': 'review-title'}).text.strip() or '',
            rating = float(item.find('i', {'data-hook': 'review-star-rating'}).text.replace('out of 5 stars', '').strip()) or None,
            body = item.find('span', {'data-hook': 'review-body'}).text.strip() or ''
            helpful = item.find('span', {'data-hook': 'helpful-vote-statement'}).text.strip() or ''

            review = {'date': date, 'title': title, 'rating': rating, 'body': body, 'helpful': helpful}

            reviewlist.append(review)
    except:
        pass

def GetAmazonReviews(pMovieID, pMovieName, pMaxPages):


        if(not os.path.exists(f'Completed/{pMovieName}-Reviews(Verified).xlsx')):
            if (not os.path.exists(f'{pMovieName}-Reviews(Verified).xlsx')):
                reviewlistverified = []

                # Get verified reviews
                for x in range(1, pMaxPages):
                    soup1 = get_soup(
                        f'https://www.amazon.com/product-reviews/{pMovieID}/ref=cm_cr_getr_d_paging_btm_next_{x}?ie=UTF8&reviewerType=avp_only_reviews&pageNumber={x}')
                    print(f'Getting page {x} out of {pMaxPages}')
                    get_reviews_unhelpful(soup1, reviewlistverified)
                    print(len(reviewlistverified))

                    if not soup1.find('li', {'class': 'a-disabled a-last'}):
                        pass
                    else:
                        break

                df = pd.DataFrame(reviewlistverified)
                df.to_excel(f'{pMovieName}-Reviews(Verified).xlsx', index=False)
        print('Fin (1/3).')

        if (not os.path.exists(f'Completed/{pMovieName}-Reviews(UnverifiedUnhelpful).xlsx')):
            if (not os.path.exists(f'{pMovieName}-Reviews(UnverifiedUnhelpful).xlsx')):
                reviewlistunverifiedunhelpful = []

                # Get unverified reviews (without helpful count)
                for y in range(1, pMaxPages):
                    soup2 = get_soup(
                        f'https://www.amazon.com/product-reviews/{pMovieID}/ref=cm_cr_getr_d_paging_btm_next_{y}?ie=UTF8&reviewerType=all_reviews&pageNumber={y}')
                    print(f'Getting page {y} out of {pMaxPages}')
                    get_reviews_unhelpful(soup2, reviewlistunverifiedunhelpful)
                    print(len(reviewlistunverifiedunhelpful))

                    if not soup2.find('li', {'class': 'a-disabled a-last'}):
                        pass
                    else:
                        break

                df = pd.DataFrame(reviewlistunverifiedunhelpful)
                df.to_excel(f'{pMovieName}-Reviews(UnverifiedUnhelpful).xlsx', index=False)
        print('Fin (2/3).')

        if (not os.path.exists(f'Completed/{pMovieName}-Reviews(Unverified).xlsx')):
            if (not os.path.exists(f'{pMovieName}-Reviews(Unverified).xlsx')):
                reviewlistunverified = []

                # Get unverified reviews (with helpful count)
                for z in range(1, pMaxPages):
                    soup3 = get_soup(
                        f'https://www.amazon.com/product-reviews/{pMovieID}/ref=cm_cr_getr_d_paging_btm_next_{z}?ie=UTF8&reviewerType=all_reviews&pageNumber={z}')
                    print(f'Getting page {z} out of {pMaxPages}')
                    get_reviews_helpful(soup3, reviewlistunverified)
                    print(len(reviewlistunverified))

                    if not soup3.find('li', {'class': 'a-disabled a-last'}):
                        pass
                    else:
                        break

                df = pd.DataFrame(reviewlistunverified)
                df.to_excel(f'{pMovieName}-Reviews(Unverified).xlsx', index=False)
        print('Fin (3/3).')

def Merge(pMovieName):

    try:
        vVerified = pd.read_excel(f'{pMovieName}-Reviews(Verified).xlsx')
        vUnverified = pd.read_excel(f'{pMovieName}-Reviews(Unverified).xlsx')
        vUnverifiedUnhelpful = pd.read_excel(f'{pMovieName}-Reviews(UnverifiedUnhelpful).xlsx')

        vMerge = vUnverifiedUnhelpful.merge(vUnverified, on=['date', 'title', 'rating'], how='left')
        vVerified['Verification'] = 1
        vMerge = vMerge.merge(vVerified, on=['date', 'title', 'rating'], how='left')

        """
        vMerge['date'] = vMerge['date'].str.replace('(\'Reviewed in the United States on ', '')
        vMerge['date'] = vMerge['date'].str.replace('\',)', '')
        vMerge['title'] = vMerge['title'].str.replace('(\'', '')
        vMerge['title'] = vMerge['title'].str.replace('\')', '')
        vMerge['title'] = vMerge['title'].str.replace('(\'', '')
        vMerge['title'] = vMerge['title'].str.replace('\')', '')
        vMerge['rating'] = vMerge['rating'].str.replace('(', '')
        vMerge['rating'] = vMerge['rating'].str.replace(',)', '')
        vMerge['helpful'] = vMerge['rating'].str.replace(' people found this helpful', '')
        vMerge['helpful'] = vMerge['rating'].str.replace('One person found this helpful', '1')
        """

        vMerge = vMerge.drop(['body_y', 'body'], axis=1)

        vMerge.to_excel(f'Consolidated-Reviews-{pMovieName}.xlsx')

    except Exception:
        print(f'Cannot merge {pMovieName}')
        pass

# Main code

vMovieKeys = pd.read_excel('Amazon Review Movie List.xlsx')

for vIndex, vRow in vMovieKeys.iterrows():
    GetAmazonReviews(vRow['Amazon ID'], vRow['Movie Name'], vRow['Max Pages'])
    Merge(vRow['Movie Name'])
