import requests  
import sys
sys.stdout.reconfigure(encoding='utf-8')
def test_query(query, is_approved=False, thread_id='test-1'):  
    res = requests.post('http://127.0.0.1:8000/api/v1/ask', json={'query': query, 'thread_id': thread_id, 'is_approved': is_approved})  
    print(f'\nQ: {query}')  
    if res.status_code == 200:  
        data = res.json()  
        print('A:', data.get('answer'))  
        print('Action:', data.get('action_taken'))  
        print('Explanation:', data.get('explanation'))  
        print('Requires Approval:', data.get('require_approval'))  
    else:  
        print('Error:', res.text)  

test_query('Who is the lead for the engineering department?')  
test_query('Flag a security issue for James Wilson.')  
test_query('Flag a security issue for James Wilson.', is_approved=True)  
test_query('Summarize the ergonomic chair specs.')  
