from pcraster import *
from pcraster.framework import *

class MyFirstModel(DynamicModel):
  def __init__(self):
    DynamicModel.__init__(self)
    setclone('randstad1.map')

  def initial(self):
    # load in randstad.map
    self.randstad = self.readmap('randstad')

    # create new categories and load these
    categories = "categories.tbl"
    self.category = lookupnominal(categories, self.randstad)
    self.report(self.category, 'category')

  def dynamic(self):
    # creating scalars
    infraScalar = scalar(self.category == 1)
    urbanScalar = scalar(self.category == 2)
    semiUrbanScalar = scalar(self.category == 3)
    recreationScalar = scalar(self.category == 4)
    agriScalar = scalar(self.category == 5)
    natureScalar = scalar(self.category == 6)
    waterScalar = scalar(self.category == 7)
    seaScalar = scalar(self.category == 8)

    # growth rates
    urbanGrowth = 0.00795 #0.0332
    semiUrbanGrowth = 0.097 #0.4430

    # change probabilities to urban
    infra2Urban = 0.0555
    semiUrban2Urban = 0.4430
    recreation2Urban = 0.0454
    agri2Urban = 0.3448
    nature2Urban = 0.0203
    water2Urban = 0.0189
    sea2Urban = 0

    # change probabilities to semi-urban
    infra2SemiUrban = 0.0160
    urban2SemiUrban = 0.0403
    recreation2SemiUrban = 0.0358
    agri2SemiUrban = 0.8240
    nature2SemiUrban = 0.0347
    water2SemiUrban = 0.0304
    sea2SemiUrban = 0.0013

    # add small random noise
    self.noise = uniform(1)/1000

    # number of urban or semi-urban neighbours
    noOfUrbanNeigh=windowtotal(urbanScalar, celllength()*3)-urbanScalar
    noOfSemiUrbanNeigh=windowtotal(semiUrbanScalar, celllength()*3)-semiUrbanScalar

    # probability of change to urban, based on cell category and neighbors
    probabilityUrbanTrans = ((infra2Urban * infraScalar) + (semiUrban2Urban * semiUrbanScalar) + \
                             (recreation2Urban * recreationScalar) + (agri2Urban * agriScalar) + \
                             (nature2Urban * natureScalar) + (water2Urban * waterScalar) + \
                             (sea2Urban * seaScalar)) * noOfUrbanNeigh + self.noise
    # probability of growth to urban based on growth rate
    probabilityUrbanGrowth = urbanGrowth

    # probability of change to semi-urban, based on cell category and neighbors
    probabilitySemiUrbanTrans = ((infra2SemiUrban * infraScalar) + (urban2SemiUrban * urbanScalar) + \
                                 (recreation2SemiUrban * recreationScalar) + (agri2SemiUrban * agriScalar) + \
                                  (nature2SemiUrban * natureScalar) + (water2SemiUrban * waterScalar) + \
                                 (sea2SemiUrban * seaScalar)) * noOfSemiUrbanNeigh + self.noise
    # probability of growth to semi-urban based on growth rate
    probabilitySemiUrbanGrowth = semiUrbanGrowth

    # first realization of cell transition to urban
    realizationUrban = uniform(1) < probabilityUrbanGrowth
    # second realization of cell transition to urban
    realizationUrban1 = pcrand(realizationUrban, uniform(1) < probabilityUrbanTrans)

    # first realization of cell transition to semi-urban
    realizationSemiUrban = uniform(1) < probabilitySemiUrbanGrowth
    # second realization of cell transition to semi-urban
    realizationSemiUrban1 = pcrand(realizationSemiUrban, uniform(1) < probabilitySemiUrbanTrans)

    # if urban and semi-urban both realized, then take transition with largest probability
    newCategory = ifthenelse(pcrand(realizationUrban1, realizationSemiUrban1),\
                             ifthenelse(probabilityUrbanTrans > probabilitySemiUrbanTrans,\
                                        nominal(2), nominal(3)),\
                                        ifthenelse(pcror(realizationUrban1, realizationSemiUrban1), nominal(99), nominal(100)))
    self.report(newCategory, 'cat')

    # set categories to right categorical number
    numberOfCat = ifthenelse(newCategory == nominal(2), nominal(2), \
                             ifthenelse(newCategory == nominal(3), nominal(3),\
                                        ifthenelse(pcrand(newCategory == nominal(99), realizationUrban1), nominal(2),\
                                                   ifthenelse(pcrand(newCategory == nominal(99), realizationSemiUrban1), nominal(3), nominal(99)))))
    self.report(numberOfCat, 'nocat')

    # subdivide new urban or semi-urban cells from the rest
    newUrbanSemi = ifthenelse(pcror(numberOfCat == 2, numberOfCat == 3), nominal(90), nominal(99))
    self.report(newUrbanSemi, 'nus')

    # if new urban or semi-urban is true, then cell is changed to new categorical number, else category stays the same
    self.report(self.category, 'category')
    self.category = ifthenelse(newUrbanSemi == nominal(90), numberOfCat, self.category)
    self.report(self.category, 'category')

    # create map for each step
    map = self.category
    self.report(map, 'randstad')

nrOfTimeSteps=20
myModel = MyFirstModel()
dynamicModel = DynamicFramework(myModel,nrOfTimeSteps)
dynamicModel.run()

  




