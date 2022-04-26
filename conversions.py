from enum import Enum

class Metric_Type(Enum):
    '''
    Metric Types.
    '''
    no_metric = 0
    dry_volume = 1
    liquid_volume = 2
    length = 3
    weight = 4

class Metric():

     def __init__(self, singular, metric_type, ratio):
        self.singular = singular
        self.metric_type = metric_type
        self.ratio = ratio

metrics = {
    'empty': Metric('', Metric_Type.no_metric, 1),
    'smidgens': Metric('smidgen', Metric_Type.dry_volume, 32),
    'pinches': Metric('pinch', Metric_Type.dry_volume, 16),
    'dashes': Metric('dash', Metric_Type.dry_volume, 8),
    'teaspoons' : Metric('teaspoon', Metric_Type.dry_volume, 1),
    'tablespoons' : Metric('tablespoon', Metric_Type.dry_volume, 0.3334),
    'cups' : Metric('cup', Metric_Type.dry_volume, 0.0616115),
    'drops':  Metric('drop', Metric_Type.liquid_volume, 591.47),
    'fluid ounces':  Metric('fluid ounce', Metric_Type.liquid_volume, 1),
    'milliliters':  Metric('milliliter', Metric_Type.liquid_volume, 29.57),
    'liters':  Metric('liter', Metric_Type.liquid_volume, 0.02957),
    'liquid cups' : Metric('liquid cup', Metric_Type.liquid_volume, 0.125),
    'pints' :  Metric('pint', Metric_Type.liquid_volume, 0.0625),
    'quarts' :  Metric('quart', Metric_Type.liquid_volume, 0.03125),
    'gallons' :  Metric('gallon', Metric_Type.liquid_volume, 0.007812),
    'inches':  Metric('inch', Metric_Type.length, 0.3937),
    'feet':  Metric('foot', Metric_Type.length, 0.0328),
    'millimeters':  Metric('millimeter', Metric_Type.length, 10),
    'centimeters':  Metric('centimeter', Metric_Type.length, 1),
    'milligrams':  Metric('milligram', Metric_Type.weight, 28350),
    'grams':  Metric('gram', Metric_Type.weight, 28.35),
    'kilograms':  Metric('kilogram', Metric_Type.weight, 0.02835),
    'ounces':  Metric('ounce', Metric_Type.weight, 1),
    'pounds':  Metric('pound', Metric_Type.weight, 0.0625)
}

def is_in_index(name):
    if get_index(name) != 'empty':
        return True
    return False

def get_index(name):
    for key, value in metrics.items():
        if key in name:
            return key
        if value.singular in name:
            return key
    return 'empty'


dry_volume_base_unit = "teaspoons"
liquid_volume_base_unit = "fluid ounces"
length_base_unit = 'centimeters'
weight_base_unit = 'ounces'

fractions = [0.75, 0.6667, 0.5, 0.3334, 0.25, 0.125, 0.0625, 0.03125, 0.015625, 0]
printable_fracts = ['', '\u00BE', '\u2154', '\u00BD', '\u2153', '\u00BC', '\u215B', '1/16', '1/32', '1/64', '']

#TODO: Quanitity conversion printing
def conversion_rounding(num):
    stripped = int(num)
    deci = num - stripped
    if deci == 0:
        return stripped
    minima = abs(deci-1)
    temp = 1
    count = 0

    for fraction in fractions:
        if(abs(deci-fraction) < minima):
            temp = fraction
            minima = abs(deci-fraction)
        else:
            break
        count += 1
    if (stripped == 0):
        stripped = ""
    converted = str(stripped) + printable_fracts[count]
    if converted == "":
        return '0'
    return converted

def convert_to_base(num, metric):
    ratio = metrics[metric].ratio
    conversion = num / ratio
    return conversion

def convert_from_base(num, new_metric):
    ratio = metrics[new_metric].ratio
    conversion = num * ratio
    return conversion

def convert_num(num, metric, new_metric):
    if(metrics[metric].metric_type != metrics[new_metric].metric_type):
        if (metrics[metric].metric_type == Metric_Type.liquid_volume and new_metric == 'cups'):
            new_metric = 'liquid cups'
        elif (metrics[new_metric].metric_type == Metric_Type.liquid_volume and metric == 'cups'):
            metric = 'liquid cups'
        else:
            raise Exception("Incompatable metric types")
    base_num = convert_to_base(num, metric)
    new_num = convert_from_base(base_num, new_metric)
    if (metrics[metric].metric_type == Metric_Type.dry_volume or metrics[metric].metric_type == Metric_Type.liquid_volume):
        return conversion_rounding(new_num)
    return str(round(new_num, 2))


# m1 = 'kilograms'
# m2 = 'grams'
# m3 = 'quarts'
# m4 = 'cups'
# print(is_in_index('gram)'))
# print(convert_num(.5, m4, m3))
