"""
Chart Generator Module
Contains logic for creating Chart.js compatible data structures
"""

from datetime import datetime


def create_chart_data(data_dict):
    """Create Chart.js compatible data structure from API response data"""
    try:
        print(f"create_chart_data called with data type: {type(data_dict)}")
        
        # Handle SINGLE exchangerate.host API response
        if isinstance(data_dict, dict) and 'query' in data_dict and 'result' in data_dict and 'info' in data_dict:
            return _create_single_exchange_rate_chart(data_dict)
        
        # Handle exchangerate.host API comparison (multiple currency conversions)
        if isinstance(data_dict, list) and len(data_dict) > 0:
            all_exchange_rates = all(
                isinstance(item, dict) and 'query' in item and 'result' in item and 'info' in item
                for item in data_dict
            )
            if all_exchange_rates:
                return _create_exchange_rate_comparison_chart(data_dict)
        
        # Handle cryptocurrency historical data (CoinGecko format)
        if isinstance(data_dict, dict) and "prices" in data_dict and isinstance(data_dict.get("prices"), list):
            return _create_crypto_historical_chart(data_dict)
        
        # Handle list of results (for comparisons)
        if isinstance(data_dict, list) and len(data_dict) > 1:
            return _create_comparison_chart(data_dict)
        
        # Check for crypto market dominance data
        if "market_cap_percentage" in str(data_dict):
            return _create_market_dominance_chart(data_dict)
        
        # Check for time series exchange rate data
        if "quotes" in data_dict and isinstance(data_dict.get("quotes"), dict):
            return _create_exchange_rate_timeseries_chart(data_dict)
        
        return None
    except Exception as e:
        print(f"Error creating chart data: {e}")
        return None


def _create_single_exchange_rate_chart(data_dict):
    """Create chart for a single exchange rate"""
    print("Detected single exchangerate.host API response")
    query = data_dict.get('query', {})
    from_curr = query.get('from', '')
    to_curr = query.get('to', '')
    rate = data_dict.get('result', 0)
    
    if from_curr and to_curr and rate:
        return {
            'type': 'bar',
            'data': {
                'labels': [f'{from_curr}/{to_curr}'],
                'datasets': [{
                    'label': f'1 {from_curr} = {rate:.4f} {to_curr}',
                    'data': [rate],
                    'backgroundColor': 'rgba(102, 126, 234, 0.6)',
                    'borderColor': 'rgb(102, 126, 234)',
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {
                        'display': True,
                        'position': 'top',
                        'labels': {'font': {'size': 14}}
                    },
                    'title': {
                        'display': True,
                        'text': f'{from_curr} to {to_curr} Exchange Rate',
                        'font': {'size': 16, 'weight': 'bold'}
                    },
                    'tooltip': {
                        'callbacks': {
                            'label': f'function(context) {{ return "1 {from_curr} = " + context.parsed.y.toFixed(4) + " {to_curr}"; }}'
                        }
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Currency Pair',
                            'font': {'size': 14, 'weight': 'bold'}
                        }
                    },
                    'y': {
                        'title': {
                            'display': True,
                            'text': 'Exchange Rate',
                            'font': {'size': 14, 'weight': 'bold'}
                        },
                        'beginAtZero': False
                    }
                }
            }
        }
    return None


def _create_exchange_rate_comparison_chart(data_list):
    """Create comparison chart for multiple exchange rates"""
    print("Detected exchangerate.host API comparison data")
    labels = []
    values = []
    
    for item in data_list:
        query = item.get('query', {})
        from_curr = query.get('from', '')
        to_curr = query.get('to', '')
        rate = item.get('result', 0)
        
        if from_curr and to_curr and rate:
            labels.append(f"{from_curr}/{to_curr}")
            values.append(rate)
            print(f"Extracted exchange rate: {from_curr}/{to_curr} = {rate}")
    
    if labels and values:
        return {
            'type': 'bar',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': 'Exchange Rate',
                    'data': values,
                    'backgroundColor': [
                        'rgba(102, 126, 234, 0.6)', 'rgba(118, 75, 162, 0.6)',
                        'rgba(237, 100, 166, 0.6)', 'rgba(255, 154, 158, 0.6)',
                        'rgba(250, 208, 196, 0.6)'
                    ],
                    'borderColor': [
                        'rgb(102, 126, 234)', 'rgb(118, 75, 162)',
                        'rgb(237, 100, 166)', 'rgb(255, 154, 158)',
                        'rgb(250, 208, 196)'
                    ],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True, 'position': 'top', 'labels': {'font': {'size': 14}}},
                    'title': {'display': True, 'text': 'Currency Exchange Rate Comparison', 'font': {'size': 16, 'weight': 'bold'}},
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return "1 " + context.label.split("/")[0] + " = " + context.parsed.y.toFixed(4) + " " + context.label.split("/")[1]; }'
                        }
                    }
                },
                'scales': {
                    'x': {'title': {'display': True, 'text': 'Currency Pairs', 'font': {'size': 14, 'weight': 'bold'}}},
                    'y': {'title': {'display': True, 'text': 'Exchange Rate Value', 'font': {'size': 14, 'weight': 'bold'}}, 'beginAtZero': False}
                }
            }
        }
    return None


def _create_crypto_historical_chart(data_dict):
    """Create line chart for cryptocurrency historical data"""
    prices = data_dict.get("prices", [])
    
    if prices:
        labels = [datetime.fromtimestamp(price[0] / 1000).strftime('%b %d, %Y') for price in prices]
        values = [price[1] for price in prices]
        
        min_price = min(values)
        max_price = max(values)
        price_change = max_price - min_price
        price_change_pct = (price_change / min_price) * 100
        
        return {
            'type': 'line',
            'data': {
                'labels': labels,
                'datasets': [{
                    'label': f'BTC Price (Range: ${min_price:,.0f} - ${max_price:,.0f})',
                    'data': values,
                    'borderColor': '#F7931A',
                    'backgroundColor': 'rgba(247, 147, 26, 0.1)',
                    'borderWidth': 2,
                    'fill': True,
                    'tension': 0.4,
                    'pointRadius': 3,
                    'pointHoverRadius': 6
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True, 'position': 'top', 'labels': {'font': {'size': 14}}},
                    'title': {
                        'display': True,
                        'text': f'Bitcoin Price History (Change: ${price_change:,.0f} / {price_change_pct:+.2f}%)',
                        'font': {'size': 16, 'weight': 'bold'}
                    },
                    'tooltip': {
                        'mode': 'index',
                        'intersect': False,
                        'callbacks': {
                            'label': 'function(context) { return "BTC: $" + context.parsed.y.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}); }',
                            'title': 'function(context) { return context[0].label; }'
                        }
                    }
                },
                'scales': {
                    'x': {
                        'title': {'display': True, 'text': 'Date', 'font': {'size': 14, 'weight': 'bold'}},
                        'ticks': {'maxRotation': 45, 'minRotation': 45}
                    },
                    'y': {
                        'title': {'display': True, 'text': 'Price in USD ($)', 'font': {'size': 14, 'weight': 'bold'}},
                        'beginAtZero': False,
                        'ticks': {'callback': 'function(value) { return "$" + value.toLocaleString(); }'}
                    }
                }
            }
        }
    return None


def _create_comparison_chart(data_list):
    """Create comparison bar chart for multiple cryptocurrencies or exchange rates"""
    labels = []
    values = []
    
    for item in data_list:
        if isinstance(item, dict):
            # Check if this is a coin price dict
            coin_found = False
            for coin, data in item.items():
                if isinstance(data, dict):
                    for currency, price in data.items():
                        if isinstance(price, (int, float)):
                            labels.append(coin.capitalize())
                            values.append(price)
                            coin_found = True
                            break
                if coin_found:
                    break
            
            # If no coin found, check if this is an exchange rate dict
            if not coin_found:
                print(f"Checking exchange rate data: {item}")
                if '_from_currency' in item and '_to_currency' in item:
                    from_curr = item['_from_currency']
                    to_curr = item['_to_currency']
                    rate = item.get('result', 0)
                    labels.append(f"{from_curr} to {to_curr}")
                    values.append(rate)
                    print(f"Added exchange rate from metadata: {from_curr} to {to_curr} = {rate}")
                elif 'query' in item and 'result' in item:
                    query = item['query']
                    from_curr = query.get('from', '')
                    to_curr = query.get('to', '')
                    rate = item.get('result', 0)
                    if from_curr and to_curr:
                        labels.append(f"{from_curr} to {to_curr}")
                        values.append(rate)
    
    print(f"Labels: {labels}, Values: {values}")
    
    if labels and values:
        is_exchange_rate = any('to' in label for label in labels)
        
        if is_exchange_rate:
            formatted_labels = []
            for label in labels:
                if ' to ' in label:
                    parts = label.split(' to ')
                    formatted_labels.append(f"{parts[0]}/{parts[1]}")
                else:
                    formatted_labels.append(label)
            y_axis_label = 'Exchange Rate Value'
            chart_title = 'Currency Exchange Rate Comparison'
            tooltip_prefix = ''
        else:
            formatted_labels = labels
            y_axis_label = 'Price in USD ($)'
            chart_title = 'Cryptocurrency Price Comparison'
            tooltip_prefix = '$'
        
        return {
            'type': 'bar',
            'data': {
                'labels': formatted_labels,
                'datasets': [{
                    'label': y_axis_label,
                    'data': values,
                    'backgroundColor': [
                        'rgba(102, 126, 234, 0.8)', 'rgba(118, 75, 162, 0.8)',
                        'rgba(247, 147, 26, 0.8)', 'rgba(34, 211, 238, 0.8)',
                        'rgba(251, 191, 36, 0.8)'
                    ],
                    'borderColor': [
                        'rgb(102, 126, 234)', 'rgb(118, 75, 162)',
                        'rgb(247, 147, 26)', 'rgb(34, 211, 238)',
                        'rgb(251, 191, 36)'
                    ],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True, 'labels': {'font': {'size': 14}}},
                    'title': {'display': True, 'text': chart_title, 'font': {'size': 16, 'weight': 'bold'}},
                    'tooltip': {
                        'callbacks': {
                            'label': f'function(context) {{ var prefix = "{tooltip_prefix}"; var decimals = {"4" if is_exchange_rate else "2"}; return context.dataset.label + ": " + prefix + context.parsed.y.toLocaleString(undefined, {{minimumFractionDigits: 2, maximumFractionDigits: decimals}}); }}'
                        }
                    }
                },
                'scales': {
                    'x': {
                        'title': {
                            'display': True,
                            'text': 'Currency Pairs' if is_exchange_rate else 'Cryptocurrencies',
                            'font': {'size': 14, 'weight': 'bold'}
                        }
                    },
                    'y': {
                        'title': {'display': True, 'text': y_axis_label, 'font': {'size': 14, 'weight': 'bold'}},
                        'beginAtZero': False
                    }
                }
            }
        }
    return None


def _create_market_dominance_chart(data_dict):
    """Create doughnut chart for market dominance"""
    market_data = data_dict.get("data", {})
    market_cap_pct = market_data.get("market_cap_percentage", {})
    
    if market_cap_pct:
        coins = [coin.upper() for coin in list(market_cap_pct.keys())]
        percentages = list(market_cap_pct.values())
        
        return {
            'type': 'doughnut',
            'data': {
                'labels': coins,
                'datasets': [{
                    'data': percentages,
                    'backgroundColor': [
                        'rgba(247, 147, 26, 0.8)', 'rgba(102, 126, 234, 0.8)',
                        'rgba(34, 211, 238, 0.8)', 'rgba(251, 191, 36, 0.8)',
                        'rgba(118, 75, 162, 0.8)', 'rgba(244, 63, 94, 0.8)'
                    ],
                    'borderColor': [
                        'rgb(247, 147, 26)', 'rgb(102, 126, 234)',
                        'rgb(34, 211, 238)', 'rgb(251, 191, 36)',
                        'rgb(118, 75, 162)', 'rgb(244, 63, 94)'
                    ],
                    'borderWidth': 2
                }]
            },
            'options': {
                'responsive': True,
                'maintainAspectRatio': False,
                'plugins': {
                    'legend': {'display': True, 'position': 'right'},
                    'title': {'display': True, 'text': 'Cryptocurrency Market Dominance'},
                    'tooltip': {
                        'callbacks': {
                            'label': 'function(context) { return context.label + ": " + context.parsed.toFixed(2) + "%"; }'
                        }
                    }
                }
            }
        }
    return None


def _create_exchange_rate_timeseries_chart(data_dict):
    """Create line chart for exchange rate time series"""
    quotes = data_dict.get("quotes", {})
    all_dates = sorted(quotes.keys())
    
    start_date = data_dict.get("start_date", "")
    end_date = data_dict.get("end_date", "")
    
    if start_date and end_date:
        dates = [date for date in all_dates if start_date <= date <= end_date]
    else:
        dates = all_dates
    
    values = [list(quotes[date].values())[0] for date in dates]
    source = data_dict.get("source", "")
    
    if dates and quotes[dates[0]]:
        target = list(quotes[dates[0]].keys())[0].replace(source, "")
    else:
        target = ""
    
    if values:
        min_rate = min(values)
        max_rate = max(values)
        avg_rate = sum(values) / len(values)
        rate_change = max_rate - min_rate
        rate_change_pct = (rate_change / min_rate) * 100 if min_rate > 0 else 0
    else:
        min_rate = max_rate = avg_rate = rate_change = rate_change_pct = 0
    
    return {
        'type': 'line',
        'data': {
            'labels': dates,
            'datasets': [{
                'label': f'1 {source} = {avg_rate:.4f} {target} (Average)',
                'data': values,
                'borderColor': 'rgb(46, 134, 171)',
                'backgroundColor': 'rgba(46, 134, 171, 0.1)',
                'borderWidth': 2,
                'fill': True,
                'tension': 0.4,
                'pointRadius': 4,
                'pointHoverRadius': 7
            }]
        },
        'options': {
            'responsive': True,
            'maintainAspectRatio': False,
            'plugins': {
                'legend': {'display': True, 'labels': {'font': {'size': 14}}},
                'title': {
                    'display': True,
                    'text': f'{source} to {target} Exchange Rate (Range: {min_rate:.4f} - {max_rate:.4f}, Change: {rate_change_pct:+.2f}%)',
                    'font': {'size': 16, 'weight': 'bold'}
                },
                'tooltip': {
                    'mode': 'index',
                    'intersect': False,
                    'callbacks': {
                        'label': f'function(context) {{ return "1 {source} = " + context.parsed.y.toFixed(4) + " {target}"; }}',
                        'title': 'function(context) { return "Date: " + context[0].label; }'
                    }
                }
            },
            'scales': {
                'x': {
                    'title': {'display': True, 'text': 'Date', 'font': {'size': 14, 'weight': 'bold'}},
                    'ticks': {'maxRotation': 45, 'minRotation': 45}
                },
                'y': {
                    'title': {
                        'display': True,
                        'text': f'Exchange Rate (1 {source} = ? {target})',
                        'font': {'size': 14, 'weight': 'bold'}
                    },
                    'beginAtZero': False,
                    'ticks': {'callback': 'function(value) { return value.toFixed(4); }'}
                }
            }
        }
    }
