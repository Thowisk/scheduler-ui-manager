from django.test import TestCase

# Create your tests here.

def testfunc(mini, maxi=10, option='slt'):
    print('1st param : '+ str(mini))
    print('2nd param : ' + str(maxi))
    print('3rd param : ' + str(option) + '\n')

params0 = {'mini': 50, 'maxi': 100}

params1 = [25,75,'oui']

testfunc(**params0)

testfunc(*params1)

testfunc(5)