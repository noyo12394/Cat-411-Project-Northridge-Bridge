export const heroMetrics = [
  { label: 'Portfolio Scale', value: '25,975', detail: 'California bridges represented in the research workflow' },
  { label: 'Decision Layers', value: '4', detail: 'HAZUS, SVI, NDVI, and ML in one comparative frame' },
  { label: 'Dashboard Goal', value: 'Real-Time', detail: 'Bridge-level interpretation for inspection planning' },
]

export const objectives = [
  {
    title: 'Core Objective',
    body:
      'Develop an interpretable machine-learning workflow that estimates bridge vulnerability from intrinsic structural attributes such as age, skew, span geometry, condition, and bridge class, while keeping hazard demand separate.',
  },
  {
    title: 'Secondary Objective',
    body:
      'Deliver an interactive dashboard that allows a user to query an individual bridge, estimate a vulnerability score, interpret likely damage severity, and prioritize inspection effort through an accessible research demo.',
  },
  {
    title: 'Integrative Goal',
    body:
      'Position HAZUS, SVI, NDVI, and machine learning as complementary layers rather than competing replacements, making it easier to compare class-based engineering logic with data-driven vulnerability ranking.',
  },
]

export const motivationPoints = [
  {
    title: 'Why ML adds value',
    body:
      'HAZUS captures event-level fragility logic and SVI captures bridge-intrinsic vulnerability, but machine learning can learn nonlinear interactions among geometry, age, condition, and structural class that are difficult to express in fixed rules alone.',
  },
  {
    title: 'Why bridge-specific variation matters',
    body:
      'Two bridges in the same hazard field can behave very differently because of rehabilitation history, skew, structural system, or deterioration. A model that keeps those differences visible can improve prioritization and interpretation.',
  },
  {
    title: 'Why comparative analysis matters',
    body:
      'The strongest research framing is not “ML replaces engineering.” It is “ML complements engineering.” The dashboard highlights where HAZUS, SVI, NDVI, and ML each fit in a practical bridge-risk workflow.',
  },
]

export const featureSelectionCards = [
  {
    title: 'Core Model Inputs',
    bullets: [
      'Year built and reconstruction timing',
      'Skew angle, spans, and maximum span length',
      'Condition rating and bridge class / HWB class',
      'SVI as a compact vulnerability descriptor',
    ],
    note: 'These are intrinsic structural variables. They support vulnerability estimation without mixing in event-specific shaking demand.',
  },
  {
    title: 'Extended Model',
    bullets: [
      'Optional NDVI change as a post-event adjustment signal',
      'Used only after an event or when change detection is available',
      'Supports interpretation, not core vulnerability ranking',
    ],
    note: 'NDVI is treated as a secondary correction layer rather than a permanent bridge attribute.',
  },
  {
    title: 'Prioritization Layer',
    bullets: [
      'ADT / traffic importance',
      'Economic disruption proxy',
      'Inspection priority and consequence ranking',
    ],
    note: 'Traffic variables belong in consequence modeling and inspection prioritization, not in the intrinsic vulnerability core model.',
  },
]

export const frameworkCards = [
  {
    name: 'HAZUS',
    role: 'Event-oriented fragility baseline',
    strength: 'Established engineering damage logic with interpretable bridge classes.',
    limitation: 'Best suited for event-specific damage estimation, not a standalone intrinsic vulnerability model.',
    connection: 'Provides baseline fragility context and benchmark damage categories.',
  },
  {
    name: 'SVI',
    role: 'Intrinsic vulnerability scoring',
    strength: 'Compresses structural vulnerability into a transparent bridge-level score.',
    limitation: 'Still depends on selected weights and may smooth over bridge-specific nonlinear effects.',
    connection: 'Acts as an interpretable feature and engineering prior for ML.',
  },
  {
    name: 'NDVI',
    role: 'Optional post-event adjustment',
    strength: 'Adds remote-sensing evidence after an event to capture disturbance not visible in inventory fields alone.',
    limitation: 'Not a permanent bridge characteristic and should not drive pre-event vulnerability ranking by itself.',
    connection: 'Useful as a post-event refinement layer and proxy-validation aid.',
  },
  {
    name: 'ML (Proposed)',
    role: 'Bridge-specific predictive layer',
    strength: 'Learns nonlinear interactions and produces bridge-level outputs that can feed a live dashboard.',
    limitation: 'Needs careful variable discipline so the model does not mix vulnerability, hazard, and consequence into one opaque score.',
    connection: 'Integrates intrinsic variables, interpretable scores, and optional post-event adjustments into one decision-support experience.',
  },
]

export const significancePoints = [
  {
    title: 'From class-based estimation to data-driven prediction',
    body:
      'A bridge portfolio is more nuanced than a single class label. Data-driven scoring helps differentiate bridges that share a nominal class but differ in age, skew, condition, and rehabilitation history.',
  },
  {
    title: 'From static analysis to interactive application',
    body:
      'A dashboard makes the workflow usable. Professors, researchers, and decision-makers can query a bridge, inspect feature contributions, and interpret how vulnerability and prioritization differ.',
  },
  {
    title: 'From isolated methods to an integrated framework',
    body:
      'The most valuable outcome is not a single metric. It is a decision-support framework that keeps HAZUS, SVI, NDVI, and ML legible as distinct yet connected tools.',
  },
]
