from Testing import ZopeTestCase as ztc
from Zope2.App import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase.layer import onsetup, onteardown
from Products.PloneTestCase import PloneTestCase as ptc
import pmr2.testing

@onsetup
def setup():
    import pmr2.annotation.citation
    fiveconfigure.debug_mode = True
    zcml.load_config('test.zcml', pmr2.testing)
    zcml.load_config('configure.zcml', pmr2.virtuoso)
    fiveconfigure.debug_mode = False
    ztc.installPackage('pmr2.virtuoso')

@onteardown
def teardown():
    pass

setup()
teardown()
ptc.setupPloneSite(products=('pmr2.virtuoso'))
