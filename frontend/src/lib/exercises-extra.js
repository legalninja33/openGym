// Exercises the shipped dataset doesn't cover.
//
// hasaneyldrm/exercises-dataset does carry five suspension-trainer entries, all with
// animations: 0805 suspended abdominal fallout, 0806 suspended push-up, 0807 suspended
// reverse crunch, 0808 suspended row and 0809 suspended split squat. Prefer those where
// they fit — they are better documented and they animate.
//
// The two below are the gaps that list leaves:
//   * 0806 is the standing variant (feet walked forward, body leaning into the handles).
//     It is not the prone, feet-elevated press, which sits in a decline position and so
//     biases the clavicular head — a different exercise, not a cue away from 0806.
//   * There is no suspended leg curl anywhere in the dataset; the closest entries are the
//     inverse/Nordic curls (0496, 0696, 0697), which are a knee-extension-side movement.
//
// A custom exercise would carry a free-text description but no numbered "How to" steps and
// would stay out of the library filters, so these live here instead, in the same shape as a
// dataset row: every EXIDX lookup, filter chip and detail sheet treats them like any other.
//
// The artwork is ours, not the dataset's: 0806's animation would be actively misleading
// here, since it shows a standing lean rather than a prone press off a bench.
// `scripts/render-trx-media.py` generates a rigged human with MPFB2 (CC0), poses it through
// IK and renders it in Blender with Freestyle outlines; `scripts/build-trx-gif.py` assembles
// the frames in the dataset's own format (180x180, 12 frames, white ground, held at each end
// position). Posing is physical rather than keyframed — the push-up pivots the body about
// the feet with the hands fixed on the handles, so the elbow bend falls out of the solver —
// which means adjusting a rep is a script edit rather than a binary hand-off.
//
// What they still lack next to the dataset's figures is musculature and the red target-muscle
// highlighting: that needs an anatomical model, and the openly licensed ones (Z-Anatomy,
// BodyParts3D) are reference geometry rather than something riggable.
//
// The media is imported rather than dropped in `public/` for two reasons. The compose file
// mounts the media volumes over `img/` and `gif/`, so anything shipped under those names is
// shadowed; and nginx caches images for 30 days, which is safe for the dataset because its
// filenames carry a content hash but would pin a stale copy of a file whose name never
// changes. Importing hands both problems to the bundler: it emits `assets/9001-<hash>.gif`,
// so editing a pose changes the URL. imgSrc/gifSrc leave a path containing a slash alone.
//
// `eq` is 'body weight' rather than a new 'suspension trainer' value on purpose: it seeds
// the bodyweight logging flag (isBodyweightEq), so a set asks for reps instead of a weight
// nobody was going to enter. Added load still works — the flag lives on the config.

import pushupGif from '../assets/trx/9001.gif'
import pushupImg from '../assets/trx/9001.jpg'
import legcurlGif from '../assets/trx/9002.gif'
import legcurlImg from '../assets/trx/9002.jpg'

export const EXTRA = [
  {
    id: '9001',
    n: 'TRX push-up (feet elevated)',
    bp: 'chest',
    eq: 'body weight',
    tg: 'pectorals',
    mg: 'triceps',
    sm: ['triceps', 'shoulders', 'abs'],
    img: pushupImg,
    gif: pushupGif,
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
    img: legcurlImg,
    gif: legcurlGif,
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
