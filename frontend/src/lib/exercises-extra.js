// Exercises the shipped dataset doesn't cover.
//
// hasaneyldrm/exercises-dataset has no suspension-trainer entries at all, so a TRX owner
// has to fall back on custom exercises — which carry a free-text description but no
// numbered "How to" steps. These fill that gap in the same shape as a dataset row, so
// every EXIDX lookup, filter chip and detail sheet treats them like any other exercise.
//
// They deliberately carry no `img`/`gif`: there is no artwork for them, and Media already
// renders a missing animation as a blank (components/Media.jsx). Everything else — body
// part, target, equipment, secondary muscles, steps — is populated so the detail sheet
// looks complete.
//
// `eq` is 'body weight' rather than a new 'suspension trainer' value on purpose: it seeds
// the bodyweight logging flag (isBodyweightEq), so a set asks for reps instead of a weight
// nobody was going to enter. Added load still works — the flag lives on the config.

export const EXTRA = [
  {
    id: '9001',
    n: 'TRX push-up (feet elevated)',
    bp: 'chest',
    eq: 'body weight',
    tg: 'pectorals',
    mg: 'triceps',
    sm: ['triceps', 'shoulders', 'abs'],
    st: [
      'Set the suspension straps so the handles hang about a hand\'s width above the floor, and place a bench behind you for your feet.',
      'Grip a handle in each hand at shoulder width and put your feet on the bench, so your body forms a straight line from head to heels.',
      'Brace your glutes and abs to lock that line — the hips must not sag or pike up at any point in the set.',
      'Lower yourself over three seconds with the elbows tucked at roughly 45 degrees from the torso, until your hands are level with your armpits or below.',
      'Pause for one second at the bottom, feeling the stretch across the chest.',
      'Press the handles forward and inward, as if squeezing them together, until the arms are extended without locking the elbows.',
      'Repeat for the desired number of repetitions.'
    ],
    desc: 'Feet on the bench put the body in a decline position, which biases the clavicular (upper) chest. The straps let the hands drop below chest level — the deficit a floor push-up cannot give.\n\nCommon mistake: hips sagging. If you cannot hold the line, take the feet off the bench and press from the floor until you can.\n\nProgression: raise the feet higher, then wear a backpack loaded with plates, then lower the handles for more range.\n\nThe straps are unstable by design. The first sessions feel harder than the load suggests and settle after two or three workouts.'
  },
  {
    id: '9002',
    n: 'TRX leg curl (foot straps)',
    bp: 'upper legs',
    eq: 'body weight',
    tg: 'hamstrings',
    mg: 'glutes',
    sm: ['glutes', 'calves', 'abs'],
    st: [
      'Set the foot cradles of the suspension trainer about 30 cm above the floor.',
      'Lie on your back with your head away from the anchor, both heels in the cradles, legs straight and arms at your sides with the palms down.',
      'Lift your hips until the body forms a straight line from shoulders to heels and squeeze the glutes — hold this bridge for the whole set.',
      'Pull the heels towards your glutes by bending the knees, letting the hips rise further as you fold.',
      'Straighten the legs over four seconds, resisting all the way — the slow phase is where the stimulus is.',
      'Repeat for the desired number of repetitions.'
    ],
    desc: 'Adds the knee-flexion work the hamstrings need, which a hip hinge such as the Romanian deadlift does not cover.\n\nCommon mistake: letting the hips drop on the way out, which turns the exercise into a stretch instead of hamstring work.\n\nProgression: four-second eccentric, then a two-second pause at full extension, then one leg at a time.\n\nHamstrings cramp easily here at first — start with eight reps and a partial range in the first session.'
  }
]
