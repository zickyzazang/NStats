import pandas as pd
import numpy as np

def total_score(items):
    return items.sum(axis=1)


def total_var(items):
    return float(items.sum(axis=1).var(ddof=1))


def item_var_sum(items):
    return float(items.var(axis=0, ddof=1).sum())


def k_by_k(items):
    nitems = items.shape[1]
    if nitems > 1:
        return (nitems/float(nitems-1))
    else: return 0


def ConverttoPandas(items):
    if type(items) == np.ndarray:
        return pd.DataFrame(items)
    elif type(items) == pd.DataFrame:
        return items
    else:
        print 'unkown data container'
        return None


def StatLOO(function, items, name, *kwargs):
    stat_without_item = pd.Series(index=items.columns, name=name)
    for item in items.columns:
        calc_stat_on = items.drop(item, axis=1)
        stat_without_item.ix[item] = function(calc_stat_on, *kwargs)
    return stat_without_item


def CronbachsAlpha(items):
    items = ConverttoPandas(items)
    return k_by_k(items)*(1-(item_var_sum(items)/total_var(items)))


def CalphaItemdeleted(items):
    items = ConverttoPandas(items)
    return StatLOO(CronbachsAlpha, items, 'Alpha if Item Deleted')


def ItemTotalCorrelation(items):
    items = ConverttoPandas(items)
    stat_without_item = pd.Series(index=items.columns, name='Item Total Correlation')
    for item in items.columns:
        total_deitemed = total_score(items) - items[item]
        stat_without_item.ix[item] = items[item].corr(total_deitemed)
    return stat_without_item

return_template = """
-------------------------------------------------------------- \n
 Cronbach's Alpha: {Calpha} \n
-------------------------------------------------------------- \n
        {iteminfo}"""

class Reliability:
    
    def _init_(self):
        self.Calpha = None
        self.CalphaItemdeleted = None
        self.ITC = None
        self.iteminfo = None
        self.dropped_items = None
        self.new_items = None
        
    def return_results(self):
        print return_template.format(Calpha=self.Calpha, iteminfo=self.iteminfo)
    
    def analyse(self, items):
        
        '''Calculates Cronbach's alpha, Item total correlation and alpha if item deleted.
        
        Parameters
        ----------
        items : pandas dataframe or numpy array
            assumes sunjeects in rows and items in columns
            
        '''
        
        self.Calpha = CronbachsAlpha(items)
        self.CalphaItemdeleted = CalphaItemdeleted(items)
        self.ITC = ItemTotalCorrelation(items)
        self.iteminfo = pd.DataFrame([self.ITC, self.CalphaItemdeleted]).T
        self.return_results()
    
    def ItemReduction(self, items):
        
        '''Iteratively remove items if that improves Cronbach's alpha. Stops when no improvement made.
        Stores new set of items in the "new_items" object.
        
        Parameters
        ----------
        items : pandas dataframe or numpy array
            assumes sunjeects in rows and items in columns
            
        '''
        items = ConverttoPandas(items)
        cids = CalphaItemdeleted(items)
        calpha = CronbachsAlpha(items)
        self.dropped_items = []
        while cids.max() > calpha:
            to_drop = cids[cids == cids.max()].index.values[0]
            self.dropped_items.append(to_drop)
            self.new_items = items.drop(self.dropped_items, axis=1)
            cids = CalphaItemdeleted(self.new_items)
            calpha = CronbachsAlpha(self.new_items)
        # Maybe a new analyses object
        print """\n
---------------------------
Results after itemreduction
---------------------------"""
        self.analyse(self.new_items)
        
