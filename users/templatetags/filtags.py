from django import template

register = template.Library()

def create_url(var):
    return f'''<a href="{var[0]}" class="text-muted"
                style="text-decoration: none;">{var[1]}</a>'''

@register.simple_tag(takes_context=True)
def breadcrumb(context):
    request = context['request']
    url_list = request.path.rstrip('/').lstrip('/').split('/')

    url_string='/'
    
    url_string_list ,url_name_list = [] , []
    if url_list[0]:
        for _url in url_list:
            url_string +=  _url + '/'
            url_string_list.append(url_string)
            url_name_list.append(_url.title())

    home = ('/','Home')
    crumb = f'''<a href="{home[0]}" class="text-muted"
                style="text-decoration: none;">{home[1]}</a>'''

    for _ in zip(url_string_list,url_name_list):
        if "Accounts" in _:
            break
        crumb = crumb + ' > ' + create_url(_) 
      
    return crumb

@register.simple_tag()
def value(val):
    return val