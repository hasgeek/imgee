from bs4 import BeautifulSoup

def get_img_id(r, img_title):
    """
    >>> r = r'''<div class="image">
    ... <span class="delete"><a href="/delete/abcd">X</a></span>
    ... <a href="/asldevi/view/abcd">
    ...     <img src="/thumbnail/abcd"/>
    ... </a>
    ... <div class="title">earth_moon_4test.gif</div>
    ... <div class="labels">
    ... </div>'''
    ...
    >>> get_img_id(r, 'earth_moon_4test.gif')
    u'abcd'
    """
    soup = BeautifulSoup(r)
    img_div = soup.find(text=img_title).findParent('div', attrs={'class': 'image'})
    x = img_div.find('a')['href']
    return x.split('/')[-1]

if __name__ == '__main__':
    import doctest
    doctest.testmod()
