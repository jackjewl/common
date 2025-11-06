

def trip(value):
    value=value.replace(' ','')
    return value

def trip_double_minus(value):
    value=value.replace('--','')
    return value
#a股股票代码
def stock_code(value):
    value=trip(value)
    value=trip_double_minus(value)
    value = re.sub(r'\D', '', value)
    return value


def column_head(value):
    value=trip(value)
    value=trip_double_minus(value)
    value=value.replace('%','')
    value=value.replace('.','')
    return value

def date(value):
    value = re.sub(r'\D', '', value)
    dt = datetime.strptime(s, "%Y%m%d")
    value = dt.strftime("%Y-%m-%d")
    return value


def str2float_string(value):
    value=trip(value)
    value=trip_doubble_minus(value)
    value = re.sub(r'[^0-9\.-]', '', value)
    value=value.replace('亿','')
    value=value.replace('万','')
    value=value.replace('百','')

    try:
        value=float(value)
        return str(value)
    except:
        return ""

def stock_name(value):

    value=trip(value)
    value=trip_double_minus(value)
    value=value.replace('-','')
    value=value.replace('*','')
    return value
