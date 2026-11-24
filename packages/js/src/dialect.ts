import { DialectResult, DialectRegion } from './types';
import { tokenize } from './stopwords';
import * as path from 'path';
import * as fs from 'fs';

let _dialectsData: any = null;

function loadDialectsJson(): any {
  if (_dialectsData) {
    return _dialectsData;
  }
  try {
    const dataPath = path.join(__dirname, '..', 'data', 'dialects.json');
    if (fs.existsSync(dataPath)) {
      const raw = fs.readFileSync(dataPath, 'utf-8');
      _dialectsData = JSON.parse(raw);
      return _dialectsData;
    }
  } catch {
    // fallback
  }
  _dialectsData = { regions: {} };
  return _dialectsData;
}

const REGIONAL_MARKERS: Record<Exclude<DialectRegion, 'GENERAL_DARJA'>, string[]> = {
  WEST: [
    'شوالا', 'شاكاين', 'شا', 'غايا', 'باغي', 'حرز', 'راك عاقل',
    'شراكم', 'كيراك', 'كيراكم', 'درك', 'حشمان', 'طاير', 'صايي',
    'طليت', 'تالمون', 'بلا مزية', 'نوليلك', 'غادي',
    'chwala', 'chakayn', 'ghaya', 'baghi', 'kirak', 'kirakom', 'drk',
    'sayi', 'bla mziya', 'ghadi'
  ],
  EAST: [
    'واشنهي', 'قداش', 'ياسر', 'ضرك', 'زي', 'باهي', 'علاشنهي',
    'واشبيك', 'كفاه', 'ضروك', 'سيرتا', 'بونة', 'عيشك', 'يعيشك',
    'على عيني', 'قندورة',
    '9dach', 'yaser', 'bahi', 'kach', '3aychek', 'wachnahi'
  ],
  CENTER: [
    'واشنو', 'حكاية', 'دروك', 'هكدا', 'هكداك', 'حوايج', 'البهجة',
    'العاصمة', 'دزاير', 'تشوف', 'مريڤل', 'حطة', 'هبال', 'كاش ما تسحق',
    'رانا هنا', 'صحيت',
    'wachnou', 'hakda', 'hakdak', 'hwaiej', 'mreguel', 'mrigel', '7atta', 'hbal'
  ],
  SOUTH: [
    'واه', 'لاه', 'حتة', 'سوف', 'ميزاب', 'غرداية', 'ادرار', 'بسكرة',
    'ورقلة', 'بشار', 'على الراس والعين', 'مرحب بيك', 'بارك الله فيك',
    'سومة زينة', 'واش حالك',
    'wah', 'lah', '7ata', 'mr7eb bik', 'zin'
  ],
};

export function getDialectMetadata(region: DialectRegion): Record<string, any> {
  const data = loadDialectsJson();
  if (data?.regions?.[region]) {
    return data.regions[region];
  }
  return {
    name_ar: region,
    tone_guide: 'دارجة جزائرية عفوية ومحترمة.',
    greetings: [],
    closure: [],
    markers: (REGIONAL_MARKERS as any)[region] || [],
  };
}

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
