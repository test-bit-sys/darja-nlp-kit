import { DialectResult, DialectRegion } from './types';
import { tokenize } from './stopwords';

const REGIONAL_MARKERS: Record<Exclude<DialectRegion, 'GENERAL_DARJA'>, string[]> = {
  WEST: [
    'شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل',
    'شراكم', 'كيراك', 'كيراكم', 'درك', 'حشمان', 'طاير',
    'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'kirakom', 'drk'
  ],
  EAST: [
    'واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي',
    'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة',
    '9dach', 'yaser', 'bahi', 'kach'
  ],
  CENTER: [
    'واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة',
    'العاصمة', 'دزاير', 'تشوف',
    'wachnou', 'hakda', 'hakdak', 'hwaiej'
  ],
  SOUTH: [
    'واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار',
    'wah', 'lah', '7ata'
  ],
};

export function detectDialect(text: string): DialectResult {
  if (!text) {
    return {
      region: 'GENERAL_DARJA',
      confidence: 0,
      detectedMarkers: [],
    };
  }

  const { tokens } = tokenize(text);
  const lowerText = text.toLowerCase();

  const scores: Record<Exclude<DialectRegion, 'GENERAL_DARJA'>, string[]> = {
    WEST: [],
    EAST: [],
    CENTER: [],
    SOUTH: [],
  };

  for (const [region, markers] of Object.entries(REGIONAL_MARKERS) as Array<[Exclude<DialectRegion, 'GENERAL_DARJA'>, string[]]>) {
    for (const marker of markers) {
      const lowerMarker = marker.toLowerCase();
      // Check in tokens or in text
      if (tokens.some((t) => t.toLowerCase() === lowerMarker) || lowerText.includes(lowerMarker)) {
        scores[region].push(marker);
      }
    }
  }

  let topRegion: DialectRegion = 'GENERAL_DARJA';
  let maxCount = 0;
  let allDetected: string[] = [];

  for (const [reg, matches] of Object.entries(scores) as Array<[Exclude<DialectRegion, 'GENERAL_DARJA'>, string[]]>) {
    if (matches.length > maxCount) {
      maxCount = matches.length;
      topRegion = reg;
      allDetected = matches;
    }
  }

  if (maxCount === 0) {
    return {
      region: 'GENERAL_DARJA',
      confidence: 0.5,
      detectedMarkers: [],
    };
  }

  const confidence = Math.min(0.99, Math.round((0.6 + maxCount * 0.15) * 100) / 100);

  return {
    region: topRegion,
    confidence,
    detectedMarkers: allDetected,
  };
}
