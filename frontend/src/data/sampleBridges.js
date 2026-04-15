export const bridgeClassOptions = [
  'HWB1', 'HWB2', 'HWB3', 'HWB4', 'HWB5', 'HWB6', 'HWB7', 'HWB8', 'HWB9', 'HWB10', 'HWB11', 'HWB12',
]

export const emptyBridgeInput = {
  yearBuilt: '',
  yearReconstructed: '',
  skewAngle: '',
  numberOfSpans: '',
  maximumSpanLength: '',
  conditionRating: '',
  bridgeClass: 'HWB3',
  sviScore: '',
  ndviChange: '',
  trafficImportance: '',
}

export const sampleBridges = [
  {
    name: 'Retrofitted Urban Overpass',
    values: {
      yearBuilt: 1968,
      yearReconstructed: 2002,
      skewAngle: 28,
      numberOfSpans: 4,
      maximumSpanLength: 142,
      conditionRating: 5,
      bridgeClass: 'HWB5',
      sviScore: 0.58,
      ndviChange: -0.08,
      trafficImportance: 38500,
    },
  },
  {
    name: 'Older Valley Connector',
    values: {
      yearBuilt: 1959,
      yearReconstructed: 1986,
      skewAngle: 41,
      numberOfSpans: 6,
      maximumSpanLength: 176,
      conditionRating: 4,
      bridgeClass: 'HWB7',
      sviScore: 0.72,
      ndviChange: -0.16,
      trafficImportance: 61200,
    },
  },
  {
    name: 'Modern Regional Arterial Bridge',
    values: {
      yearBuilt: 2008,
      yearReconstructed: '',
      skewAngle: 9,
      numberOfSpans: 3,
      maximumSpanLength: 115,
      conditionRating: 7,
      bridgeClass: 'HWB2',
      sviScore: 0.29,
      ndviChange: '',
      trafficImportance: 18400,
    },
  },
]
