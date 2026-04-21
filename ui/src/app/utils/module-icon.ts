export interface ModuleIcon {
  icon: string;   // FA class string e.g. 'fa-solid fa-clock', empty string = use letter avatar
  letter: string; // first 2 chars of title, shown when icon is ''
  bg: string;     // tile background color
  fg: string;     // icon / letter color
}

// Deterministic palette — 8 hues that complement the app's okl dark theme
const PALETTES: Array<{ bg: string; fg: string }> = [
  { bg: 'oklch(0.26 0.09 265)', fg: 'oklch(0.74 0.13 265)' }, // violet
  { bg: 'oklch(0.26 0.08 240)', fg: 'oklch(0.74 0.12 240)' }, // blue
  { bg: 'oklch(0.26 0.07 200)', fg: 'oklch(0.72 0.09 200)' }, // teal
  { bg: 'oklch(0.26 0.08 155)', fg: 'oklch(0.74 0.11 155)' }, // green
  { bg: 'oklch(0.26 0.09 75)',  fg: 'oklch(0.87 0.10 75)'  }, // amber
  { bg: 'oklch(0.26 0.10 50)',  fg: 'oklch(0.80 0.13 50)'  }, // orange
  { bg: 'oklch(0.26 0.09 22)',  fg: 'oklch(0.72 0.13 22)'  }, // red
  { bg: 'oklch(0.26 0.08 340)', fg: 'oklch(0.74 0.11 340)' }, // pink
];

// [pattern, FA-class] — tested against lowercased `title + ' ' + directory`
const KEYWORD_ICONS: Array<[RegExp, string]> = [
  [/\bclock\b|wordclock|analog.?clock/, 'fa-solid fa-clock'],
  [/\bweather\b|forecast|temperature|humidity/, 'fa-solid fa-cloud-sun'],
  [/\brain\b|snow|ice|precipitation/, 'fa-solid fa-cloud-rain'],
  [/\bwind\b|air.?quality|pollution|pollen/, 'fa-solid fa-wind'],
  [/\bsun\b|uv.?index|solar/, 'fa-solid fa-sun'],
  [/\bmoon\b|lunar/, 'fa-solid fa-moon'],
  [/calendar|event|agenda|schedule/, 'fa-solid fa-calendar-days'],
  [/\bnews\b|\brss\b|feed|headline/, 'fa-solid fa-newspaper'],
  [/spotify|lastfm|\bmusic\b|audio|song|playlist/, 'fa-solid fa-music'],
  [/transit|subway|metro|\btrain\b|\bbus\b|tram|commute/, 'fa-solid fa-train-subway'],
  [/traffic|navigation|directions|\broute\b/, 'fa-solid fa-route'],
  [/\bmap\b|location|geocod/, 'fa-solid fa-map-location-dot'],
  [/\bflight\b|\bplane\b|aviation|airport/, 'fa-solid fa-plane'],
  [/\bcar\b|parking|vehicle/, 'fa-solid fa-car'],
  [/stock|finance|crypto|bitcoin|market|portfolio|forex|currency|coinbase/, 'fa-solid fa-chart-line'],
  [/\bcoin\b|\bwallet\b/, 'fa-solid fa-coins'],
  [/sport|football|soccer|basketball|tennis|nfl|nba|nhl|mlb|\bscore\b/, 'fa-solid fa-trophy'],
  [/fitness|workout|exercise|pedometer|step.count/, 'fa-solid fa-heart-pulse'],
  [/covid|virus|pandemic/, 'fa-solid fa-virus'],
  [/\balert\b|notification|pager/, 'fa-solid fa-bell'],
  [/compliment|affirmation|inspire|motivat/, 'fa-solid fa-comment-dots'],
  [/\bquote\b|saying/, 'fa-solid fa-quote-left'],
  [/photo|gallery|picture|flickr|instagram|slideshow/, 'fa-solid fa-images'],
  [/\bvideo\b|youtube|stream|twitch|plex|\bmedia\b/, 'fa-solid fa-play'],
  [/home.?assist|homekit|\biot\b|hue|\bsensor\b/, 'fa-solid fa-house-signal'],
  [/\beye\b|face.detect|track/, 'fa-solid fa-eye'],
  [/background|wallpaper|screensaver/, 'fa-solid fa-panorama'],
  [/twitter|tweet/, 'fa-brands fa-x-twitter'],
  [/telegram/, 'fa-brands fa-telegram'],
  [/github/, 'fa-brands fa-github'],
  [/network|pihole|\bdns\b|\bip.addr/, 'fa-solid fa-network-wired'],
  [/system.?info|cpu\b|memory|\bram\b|\btemp\b|monitor|sysinfo/, 'fa-solid fa-microchip'],
  [/countdown|timer|stopwatch/, 'fa-solid fa-stopwatch'],
  [/\bbook\b|library|\bread\b|reading/, 'fa-solid fa-book'],
  [/\bgame\b|chess|puzzle/, 'fa-solid fa-gamepad'],
  [/plant|garden|seedling/, 'fa-solid fa-seedling'],
  [/sleep|\bwake\b|bedtime/, 'fa-solid fa-bed'],
  [/todo|\btask\b|kanban|trello/, 'fa-solid fa-list-check'],
  [/voice|alexa|assistant|microphone/, 'fa-solid fa-microphone'],
  [/horoscope|astro|zodiac/, 'fa-solid fa-star'],
  [/\bword\b|text|font/, 'fa-solid fa-font'],
  [/life.?cycle|habit/, 'fa-solid fa-rotate'],
];

// Category-level fallback icons
const CATEGORY_ICONS: Array<[RegExp, string]> = [
  [/finance|stock|banking/, 'fa-solid fa-chart-line'],
  [/entertainment|media/, 'fa-solid fa-film'],
  [/education|learning/, 'fa-solid fa-graduation-cap'],
  [/news/, 'fa-solid fa-newspaper'],
  [/health|wellness/, 'fa-solid fa-heart-pulse'],
  [/sport|fitness/, 'fa-solid fa-trophy'],
  [/weather/, 'fa-solid fa-cloud-sun'],
  [/transport/, 'fa-solid fa-car'],
  [/social/, 'fa-solid fa-users'],
  [/productiv/, 'fa-solid fa-list-check'],
  [/smart.home|iot|home.automat/, 'fa-solid fa-house-signal'],
  [/utility|tool|system/, 'fa-solid fa-wrench'],
];

function hashCode(s: string): number {
  let h = 5381;
  for (let i = 0; i < s.length; i++) {
    h = ((h << 5) + h) ^ s.charCodeAt(i);
  }
  return Math.abs(h);
}

export function getModuleIcon(pkg: { title: string; category?: string; directory?: string }): ModuleIcon {
  const probe = `${pkg.title} ${pkg.directory ?? ''}`.toLowerCase();
  const cat   = (pkg.category ?? '').toLowerCase();

  const palette = PALETTES[hashCode(pkg.title) % PALETTES.length];

  // 1. keyword match on title + directory
  for (const [re, icon] of KEYWORD_ICONS) {
    if (re.test(probe)) {
      return { icon, letter: '', bg: palette.bg, fg: palette.fg };
    }
  }

  // 2. category match
  for (const [re, icon] of CATEGORY_ICONS) {
    if (re.test(cat)) {
      return { icon, letter: '', bg: palette.bg, fg: palette.fg };
    }
  }

  // 3. letter avatar fallback
  const letter = pkg.title.trim().slice(0, 2).toUpperCase();
  return { icon: '', letter, bg: palette.bg, fg: palette.fg };
}
