#include <iostream>
#include <string>
#include <map>
//#include <random>
#include <ctime>
#include <cstdlib>


using namespace std;

/* this program is product random number with stockcode */

#define RANDOM_COUNT_MAX 1000000
#define RANDOM_COUNT_MIN 10000
#define RANDOM_CODE_MAX (9999)

#define SH_CODE_PREFIX 600
#define SZ_CODE_PREFIX 00
#define CY_CODE_PREFIX 300
#define CODE_SUFFIX_MAX 999

#define random_test  (srand((unsigned int) time(0)))

int code_random()
{
    int code = 0;
    int prefix = SH_CODE_PREFIX;
    map<int,int> mCode;
    map<int,int>::iterator m_it;
    
    srand((unsigned int) time(0));
    for (int i = 0; i < RANDOM_COUNT_MAX; i++){
        code = rand() % RANDOM_CODE_MAX;
        if (code < CODE_SUFFIX_MAX){
            code += SH_CODE_PREFIX * 1000;
        }
        m_it = mCode.find(code);
        if (m_it == mCode.end()){
            mCode.insert(pair<int,int> (code, 1));
        }
        else{
            m_it->second += 1;
            //m_it[code] += 1;
        }
    }

    int count = 0;
    for (m_it = mCode.begin();  m_it != mCode.end(); m_it++){
        // cout<< m_it->first << " "  << m_it->second << ";" ;
        if (count < m_it->second){
            count = m_it->second;
            code = m_it->first;
         }
    }
    cout << code << " " << count << endl;
    return code;
}

int main(){
    cout << "stockcode  " << code_random() << endl; 
    return 0;
}
