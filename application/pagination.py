import math

def get_pagination(page: int, take: int, total: int) -> list:
    """
    Return list of pages depends of curent page
    and total articles stored in db
    """
    
    pagelist = []
    
    if total == 0 or total < take:
        return []

    all_pages = math.ceil(total/take)

    if page-3 > 1 and page-3 < all_pages:
        pagelist.append("1")
    
    for i in range(all_pages):
        if i !=0 and i >= page-3 and i <= page+3:
            pagelist.append(str(i))
            continue
    
        if i != 0 and i >= page-30 and i <= page+30 and i%10 == 0:
            pagelist.append(str(i))

    if all_pages%10 != 0:
        pagelist.append(str(all_pages))

    return pagelist