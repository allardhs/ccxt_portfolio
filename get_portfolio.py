"""
	
	-----------------------------
	ccxt get porfolio
	-----------------------------
    
"""

""" imports """

# system libraries
import os, sys, getopt, json, traceback
from datetime import datetime

# subscripts
#from preferences import prefs, paths, credentials, portfolio_override

# tool to parse ini files
from configparser import ConfigParser

# ccxt
import ccxt

# forex
#from forex_python.converter import CurrencyRates
from forex_python_temp.converter import CurrencyRates

# pycoingecko
from pycoingecko import CoinGeckoAPI

""" defines """

currencies = [ 'EUR', 'USD', 'CHF' ]

""" functions """

def dict_merge( d1, d2 ) :
    for k, v in d1.items() :
        if k in d2 :
            d2[k] = dict_merge( v, d2[k] )
    d1.update( d2 )
    return d1

""" banner """

start_time = datetime.now()

print()
print( "==============================================" )
print( "-=^=-        GET_PORTFOLIO SCRIPT        -=^=-" )
print( "----------------------------------------------" )
print( "     (started at: " + start_time.strftime( "%Y-%m-%d %H:%M:%S" ) + ")" )
print( "----------------------------------------------" )
print( " options:                                     " )
print()
print( "  (empty)           : run normally            " )
print()
print( "  -h / --help       : show help screen        " )
print( "  -v / --verbose    : show verbose output     " )
print()
print( "----------------------------------------------" )

""" arguments and help """

def showhelp() :
    print()
    print( " help...                                      " )
    print()
    print( "==============================================" )
    print()

try :
    opts, args = getopt.getopt( sys.argv[1:], 'vh', [ 'verbose', 'help' ] )
except getopt.GetoptError :
    showhelp()
    sys.exit(2)

verbose = False

for opt, arg in opts :
    if opt in ( '-v', '--verbose' ) :
        verbose = True
    elif opt in ( '-h', '--help' ) :
        showhelp()
        sys.exit(2)
    else :
        showhelp()
        sys.exit(2)

""" parse config ini files """

config = ConfigParser()
config.read( 'keys.ini' )
credentials = {}
for each_section in config.sections() :
    credentials[ each_section ] = {}
    for ( each_key, each_val ) in config.items( each_section ) :
        credentials[ each_section ][ each_key ] = each_val
#print( json.dumps( credentials, indent=2 ) )

config = ConfigParser()
config.read( 'prefs.ini' )
prefs = {}
for each_section in config.sections() :
    prefs[ each_section ] = {}
    for ( each_key, each_val ) in config.items( each_section ) :
        prefs[ each_section ][ each_key ] = each_val
#print( json.dumps( prefs, indent=2 ) )

config = ConfigParser()
config.read( 'portfolio_overrides.ini' )
portfolio_override = {}
for each_section in config.sections() :
    portfolio_override[ each_section ] = {}
    for ( each_key, each_val ) in config.items( each_section ) :
        portfolio_override[ each_section ][ each_key ] = json.loads( each_val )
#print( json.dumps( portfolio_override, indent=2 ) )

""" get coin metadata from coingecko """

cg = CoinGeckoAPI()
coingecko_list_1 = cg.get_coins_markets( prefs[ "prefs" ][ "base_currency" ].lower(), order = 'market_cap_desc', per_page = 250, page = 1, price_change_percentage = '1h%2C24h%2C7d%2C30d%2C1y' )
coingecko_list_2 = cg.get_coins_markets( prefs[ "prefs" ][ "base_currency" ].lower(), order = 'market_cap_desc', per_page = 250, page = 2, price_change_percentage = '1h%2C24h%2C7d%2C30d%2C1y' )
coingecko_list_3 = cg.get_coins_markets( prefs[ "prefs" ][ "base_currency" ].lower(), order = 'market_cap_desc', per_page = 250, page = 3, price_change_percentage = '1h%2C24h%2C7d%2C30d%2C1y' )
coingecko_list_4 = cg.get_coins_markets( prefs[ "prefs" ][ "base_currency" ].lower(), order = 'market_cap_desc', per_page = 250, page = 4, price_change_percentage = '1h%2C24h%2C7d%2C30d%2C1y' )

""" fetch currency conversion factors and add to balances dict """

balances = {
    'crypto': {},
    'fiat': {},
    'currencies': {},
    'totals': 0
}

c = CurrencyRates()
for currency in currencies :
    if currency == prefs[ "prefs" ][ "base_currency" ] :
        balances[ 'currencies' ][ currency + prefs[ "prefs" ][ "base_currency" ] ] = 1
    else :
        value = c.convert( currency, prefs[ "prefs" ][ "base_currency" ], 1 )
        balances[ 'currencies' ][ currency + prefs[ "prefs" ][ "base_currency" ] ] = float(value)
#print( json.dumps( balances, indent=2 ) )

""" add overriding balances with values from portfolio_override in preferences.py """

for exchange in portfolio_override[ 'fiat' ] :
    for coin in portfolio_override[ 'fiat' ][ exchange ] :
        
        if not coin in balances[ 'fiat' ] :
            balances[ 'fiat' ][ coin ] = {}
        if not 'on_exchange' in balances[ 'fiat' ][ coin ] :
            balances[ 'fiat' ][ coin ][ 'on_exchange' ] = {}
        if not exchange in balances[ 'fiat' ][ coin ][ 'on_exchange' ] :
            balances[ 'fiat' ][ coin ][ 'on_exchange' ][ exchange ] = {}
        
        p = balances['currencies'][ str(coin) + prefs[ "prefs" ][ 'base_currency' ] ]
        q = portfolio_override[ 'fiat' ][ exchange ][ coin ]
        
        balances[ 'fiat' ][ coin ][ 'on_exchange' ][ exchange ][ 'balance' ] = q
        balances[ 'fiat' ][ coin ][ 'on_exchange' ][ exchange ][ 'latest_price' ] = p
        balances[ 'fiat' ][ coin ][ 'on_exchange' ][ exchange ][ 'latest_value' ] = p * q

for exchange in portfolio_override[ 'crypto' ] :
    
    if verbose :
        print( exchange, ":" )
    
    for coin in portfolio_override[ 'crypto' ][ exchange ] :
        
        p = 0
        q = 0
        
        if not coin in balances[ 'crypto' ] :
            balances[ 'crypto' ][ coin ] = {}
        if not 'on_exchange' in balances[ 'crypto' ][ coin ] :
            balances[ 'crypto' ][ coin ][ 'on_exchange' ] = {}
        if not exchange in balances[ 'crypto' ][ coin ][ 'on_exchange' ] :
            balances[ 'crypto' ][ coin ][ 'on_exchange' ][ exchange ] = {}
        
        for coingecko_listing in coingecko_list_4 :
            if coingecko_listing[ 'symbol' ].lower() == coin.lower() :
                p = float(coingecko_listing[ 'current_price' ])
        for coingecko_listing in coingecko_list_3 :
            if coingecko_listing[ 'symbol' ].lower() == coin.lower() :
                p = float(coingecko_listing[ 'current_price' ])
        for coingecko_listing in coingecko_list_2 :
            if coingecko_listing[ 'symbol' ].lower() == coin.lower() :
                p = float(coingecko_listing[ 'current_price' ])
        for coingecko_listing in coingecko_list_1 :
            if coingecko_listing[ 'symbol' ].lower() == coin.lower() :
                p = float(coingecko_listing[ 'current_price' ])
        
        q = portfolio_override[ 'crypto' ][ exchange ][ coin ]
        
        balances[ 'crypto' ][ coin ][ 'on_exchange' ][ exchange ][ 'balance' ] = q
        balances[ 'crypto' ][ coin ][ 'on_exchange' ][ exchange ][ 'latest_price' ] = p
        balances[ 'crypto' ][ coin ][ 'on_exchange' ][ exchange ][ 'latest_value' ] = p * q
        
        if verbose :
            print( " > " + str(coin) + ": q[" + str(round(q,2)) + "] @ p[" + str(round(p,2)) + "] = " + str(prefs[ "prefs" ][ "base_currency" ].lower()) + " [" + str(round(p * q,2)) + "]")
#print( json.dumps( balances, indent=2 ) )
#exit()

""" fetch balances on all your exchanges """
# https://pypi.org/project/ccxt/
# list of all available exchanges and their IDs: print( ccxt.exchanges )
# check which credentials are required: print( exchange.requiredCredentials )

for exchange_id in credentials :
    
    if verbose :
        print( exchange_id, ":" )
    
    exchange_class = getattr( ccxt, exchange_id )
    if 'api_key' in credentials[ exchange_id ] and 'secret' in credentials[ exchange_id ] and 'password' in credentials[ exchange_id ] :
        exchange = exchange_class({
            'apiKey': credentials[ exchange_id ][ 'api_key' ],
            'secret': credentials[ exchange_id ][ 'secret' ],
            'password': credentials[ exchange_id ][ 'password' ],
        })
    elif 'api_key' in credentials[ exchange_id ] and 'secret' in credentials[ exchange_id ] :
        exchange = exchange_class({
            'apiKey': credentials[ exchange_id ][ 'api_key' ],
            'secret': credentials[ exchange_id ][ 'secret' ],
        })
    elif 'api_key' in credentials[ exchange_id ] :
        exchange = exchange_class({
            'apiKey': credentials[ exchange_id ][ 'api_key' ],
        })
    #print( exchange.requiredCredentials )
    
    loop = True
    params = {}
    try:
        while loop == True :
            
            balance = exchange.fetchBalance( params = params )
            #print( balance )
            
            pagination = exchange.safeValue( balance['info'], 'pagination' )
            #print( pagination )
            if pagination is None :
                #print( "quitting now.." )
                loop = False
            else :
                next_starting_after = exchange.safeString( pagination, 'next_starting_after' )
                #print( next_starting_after )
                if next_starting_after is not None :
                    params[ 'starting_after' ] = next_starting_after
                else :
                    loop = False
            
            for stash in balance['total'] :
                #print( stash, balance['total'][stash] )
                
                p = 0
                q = 0
                
                if balance['total'][stash] > 0 :
                    
                    if verbose :
                        print( " - " + str(stash) + ": [" + str(balance['total'][stash]) + "]\r", end="" )
                    if str(stash) in currencies :
                        
                        if not str(stash) in balances['fiat'] :
                            balances['fiat'][ str(stash) ] = {}
                        if not 'on_exchange' in balances['fiat'][ str(stash) ] :
                            balances['fiat'][ str(stash) ]['on_exchange'] = {}
                        if not exchange_id in balances['fiat'][ str(stash) ]['on_exchange'] :
                            balances['fiat'][ str(stash) ]['on_exchange'][ exchange_id ] = {}
                        
                        p = balances['currencies'][ str(stash) + prefs[ "prefs" ][ 'base_currency' ] ]
                        q = balance['total'][stash]
                        balances['fiat'][ str(stash) ]['on_exchange'][ exchange_id ]['balance'] = q
                        balances['fiat'][ str(stash) ]['on_exchange'][ exchange_id ]['latest_price'] = p
                        balances['fiat'][ str(stash) ]['on_exchange'][ exchange_id ]['latest_value'] = p * q
                        
                        #balances['fiat'][ str(stash) ][ exchange_id ]['last_updated'] = datetime.now().strftime( "%Y-%m-%d %H:%M" )
                        
                    else :
                        
                        if not str(stash) in balances['crypto'] :
                            balances['crypto'][ str(stash) ] = {}
                        
                        if not 'on_exchange' in balances['crypto'][ str(stash) ] :
                            balances['crypto'][ str(stash) ]['on_exchange'] = {}
                        if not exchange_id in balances['crypto'][ str(stash) ]['on_exchange'] :
                            balances['crypto'][ str(stash) ]['on_exchange'][ exchange_id ] = {}
                            
                        try :
                            p = float(exchange.fetchTicker( str(stash) + '/USD' )['last']) * balances['currencies'][ 'USD' + prefs[ "prefs" ][ 'base_currency' ] ]
                        except :
                            try :
                                p = float(exchange.fetchTicker( str(stash) + '/USDT' )['last']) * balances['currencies'][ 'USD' + prefs[ "prefs" ][ 'base_currency' ] ]
                            except :
                                p = 0
                        q = balance['total'][stash]
                        balances['crypto'][ str(stash) ]['on_exchange'][ exchange_id ]['balance'] = q
                        balances['crypto'][ str(stash) ]['on_exchange'][ exchange_id ]['latest_price'] = p
                        balances['crypto'][ str(stash) ]['on_exchange'][ exchange_id ]['latest_value'] = p * q
                    
                    if verbose :
                        print( " > " + str(stash) + ": q[" + str(round(q,2)) + "] @ p[" + str(round(p,2)) + "] = " + str(prefs[ "prefs" ][ "base_currency" ].lower()) + " [" + str(round(p * q,2)) + "]")
                    
    except :
        print( "Error: ", end="" )
        print( traceback.format_exc() )

"""" merge overriding inputs from preferences """

if prefs[ "paths" ][ 'presearch_json_path' ] and prefs[ "paths" ][ 'presearch_json_path' ].strip() :
    
    with open( prefs[ "paths" ][ 'presearch_json_path' ] + 'scores.txt') as json_file :
        data = json.load(json_file)
    q = data[ 'total' ]
    p = 0
    
    if verbose :
        print( "presearch :" )
        print( " - PRE: [" + str(q) + "]\r", end="" )
    for coingecko_listing in coingecko_list_4 :
        if coingecko_listing[ 'symbol' ] == "pre" :
            p = float(coingecko_listing[ 'current_price' ])
    for coingecko_listing in coingecko_list_3 :
        if coingecko_listing[ 'symbol' ] == "pre" :
            p = float(coingecko_listing[ 'current_price' ])
    for coingecko_listing in coingecko_list_2 :
        if coingecko_listing[ 'symbol' ] == "pre" :
            p = float(coingecko_listing[ 'current_price' ])
    for coingecko_listing in coingecko_list_1 :
        if coingecko_listing[ 'symbol' ] == "pre" :
            p = float(coingecko_listing[ 'current_price' ])
    
    more_balances = {
        "crypto": {
            "PRE": {
                "on_exchange": {
                    "presearch": {
                        "balance": q,
                        "latest_price": p,
                        "latest_value": p * q,
                    }
                }
            }
        }
    }
    
    if verbose :
        print( " > PRE: [" + str(q) + "] @ [" + str(round(p,2)) + "] = [" + str(round(p * q,2)) + "]")
    
    balances = dict_merge( balances, more_balances )

""" sum up totals per currency, get pricing, and calculate values """

#print( json.dumps( balances, indent=2 ) )
for type in balances :
    if type == 'crypto' or type == 'fiat' :
        for coin in balances[type] :
            
            balances[type][coin][ 'balance' ] = sum( d['balance'] for d in balances[type][coin]['on_exchange'].values() if d )
            balances[type][coin][ 'latest_value' ] = sum( d['latest_value'] for d in balances[type][coin]['on_exchange'].values() if d )
            
            for exch in balances[type][coin]['on_exchange'] :
                balances['totals'] += balances[type][coin]['on_exchange'][exch]['latest_value']

""" order coins in balances dict by value """

balances['crypto'] = { k: v for k, v in sorted( balances['crypto'].items(), key=lambda item: item[1]['latest_value'], reverse=True ) }
balances['fiat'] = { k: v for k, v in sorted( balances['fiat'].items(), key=lambda item: item[1]['latest_value'], reverse=True ) }

""" add coin metadata from coingecko """

for coin_to_track in balances['crypto'] :
    for coingecko_listing in coingecko_list_4 :
        if coingecko_listing[ 'symbol' ].lower() == coin_to_track.lower() :
            balances['crypto'][ coin_to_track ][ 'name' ] = coingecko_listing[ 'name' ]
            balances['crypto'][ coin_to_track ][ 'gecko_id' ] = coingecko_listing[ 'id' ]
            balances['crypto'][ coin_to_track ][ 'image' ] = coingecko_listing[ 'image' ]
            balances['crypto'][ coin_to_track ][ 'ath' ] = coingecko_listing[ 'ath' ]
            balances['crypto'][ coin_to_track ][ 'latest_price' ] = coingecko_listing[ 'current_price' ]
            balances['crypto'][ coin_to_track ][ 'delta_1h' ] = coingecko_listing[ 'price_change_percentage_1h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_24h' ] = coingecko_listing[ 'price_change_percentage_24h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_7d' ] = coingecko_listing[ 'price_change_percentage_7d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_30d' ] = coingecko_listing[ 'price_change_percentage_30d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_1y' ] = coingecko_listing[ 'price_change_percentage_1y_in_currency' ]
    for coingecko_listing in coingecko_list_3 :
        if coingecko_listing[ 'symbol' ].lower() == coin_to_track.lower() :
            balances['crypto'][ coin_to_track ][ 'name' ] = coingecko_listing[ 'name' ]
            balances['crypto'][ coin_to_track ][ 'gecko_id' ] = coingecko_listing[ 'id' ]
            balances['crypto'][ coin_to_track ][ 'image' ] = coingecko_listing[ 'image' ]
            balances['crypto'][ coin_to_track ][ 'ath' ] = coingecko_listing[ 'ath' ]
            balances['crypto'][ coin_to_track ][ 'latest_price' ] = coingecko_listing[ 'current_price' ]
            balances['crypto'][ coin_to_track ][ 'delta_1h' ] = coingecko_listing[ 'price_change_percentage_1h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_24h' ] = coingecko_listing[ 'price_change_percentage_24h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_7d' ] = coingecko_listing[ 'price_change_percentage_7d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_30d' ] = coingecko_listing[ 'price_change_percentage_30d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_1y' ] = coingecko_listing[ 'price_change_percentage_1y_in_currency' ]
    for coingecko_listing in coingecko_list_2 :
        if coingecko_listing[ 'symbol' ].lower() == coin_to_track.lower() :
            balances['crypto'][ coin_to_track ][ 'name' ] = coingecko_listing[ 'name' ]
            balances['crypto'][ coin_to_track ][ 'gecko_id' ] = coingecko_listing[ 'id' ]
            balances['crypto'][ coin_to_track ][ 'image' ] = coingecko_listing[ 'image' ]
            balances['crypto'][ coin_to_track ][ 'ath' ] = coingecko_listing[ 'ath' ]
            balances['crypto'][ coin_to_track ][ 'latest_price' ] = coingecko_listing[ 'current_price' ]
            balances['crypto'][ coin_to_track ][ 'delta_1h' ] = coingecko_listing[ 'price_change_percentage_1h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_24h' ] = coingecko_listing[ 'price_change_percentage_24h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_7d' ] = coingecko_listing[ 'price_change_percentage_7d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_30d' ] = coingecko_listing[ 'price_change_percentage_30d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_1y' ] = coingecko_listing[ 'price_change_percentage_1y_in_currency' ]
    for coingecko_listing in coingecko_list_1 :
        if coingecko_listing[ 'symbol' ].lower() == coin_to_track.lower() :
            balances['crypto'][ coin_to_track ][ 'name' ] = coingecko_listing[ 'name' ]
            balances['crypto'][ coin_to_track ][ 'gecko_id' ] = coingecko_listing[ 'id' ]
            balances['crypto'][ coin_to_track ][ 'image' ] = coingecko_listing[ 'image' ]
            balances['crypto'][ coin_to_track ][ 'ath' ] = coingecko_listing[ 'ath' ]
            balances['crypto'][ coin_to_track ][ 'latest_price' ] = coingecko_listing[ 'current_price' ]
            balances['crypto'][ coin_to_track ][ 'delta_1h' ] = coingecko_listing[ 'price_change_percentage_1h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_24h' ] = coingecko_listing[ 'price_change_percentage_24h_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_7d' ] = coingecko_listing[ 'price_change_percentage_7d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_30d' ] = coingecko_listing[ 'price_change_percentage_30d_in_currency' ]
            balances['crypto'][ coin_to_track ][ 'delta_1y' ] = coingecko_listing[ 'price_change_percentage_1y_in_currency' ]

""" fetch N days of price history for each coin from coingecko """

for coin_to_track in balances['crypto'] :
    if 'gecko_id' in balances[ 'crypto' ][ coin_to_track ] :
        balances[ 'crypto' ][ coin_to_track ][ 'price_history' ] = cg.get_coin_market_chart_by_id( balances[ 'crypto' ][ coin_to_track ][ 'gecko_id' ], prefs[ "prefs" ][ 'base_currency' ].lower(), prefs[ "prefs" ][ 'price_history_in_days' ], interval = 'daily'  )[ 'prices' ]

""" dump json to disk """

#print( json.dumps( balances, indent=2 ) )
if not os.path.exists( prefs[ "paths" ][ 'json_output_path' ] ) :
    os.makedirs( prefs[ "paths" ][ 'json_output_path' ] )
if not os.path.exists( prefs[ "paths" ][ 'json_output_path' ] + "crypto_portfolio.txt" ) :
    open( prefs[ "paths" ][ 'json_output_path' ] + "crypto_portfolio.txt", "w" ).close()
with open( prefs[ "paths" ][ 'json_output_path' ] + "crypto_portfolio.txt", "w") as output_file :
    json.dump( balances, output_file )

""" end banner, and show how long the script ran for """

print()
print( "----------------------------------------------" )
print( "     (Duration: {}".format( datetime.now() - start_time ) + ")" )
print( "==============================================" )
print()
