/** Synthetic teaching data only; no observations or target prices are modelled. */
export const TRAINING = Object.freeze([
  { area: 40, rooms: 1, district: '中心' },
  { area: 60, rooms: 2, district: '近郊' },
  { area: 80, rooms: 2, district: '远郊' },
  { area: 100, rooms: 3, district: '中心' },
  { area: 120, rooms: 4, district: '近郊' },
].map(Object.freeze));

/** Fit only on the training split; transformation never changes these statistics. */
export function fit(training) {
  if (!Array.isArray(training) || training.length < 2) {
    throw new TypeError('Training requires at least two complete rows.');
  }
  for (const row of training) {
    if (!row || !Number.isFinite(row.area) || row.area <= 0 ||
        !Number.isInteger(row.rooms) || row.rooms <= 0 ||
        typeof row.district !== 'string' || !row.district.trim()) {
      throw new TypeError('Training rows require positive area, positive integer rooms and a district.');
    }
  }
  const areas = training.map(row => row.area).sort((a, b) => a - b);
  const min = areas[0];
  const max = areas.at(-1);
  if (min === max) throw new RangeError('This teaching scaler requires a nonzero training range.');
  const middle = Math.floor(areas.length / 2);
  const median = areas.length % 2 ? areas[middle] : (areas[middle - 1] + areas[middle]) / 2;
  return Object.freeze({
    median, min, max,
    categories: Object.freeze([...new Set(training.map(row => row.district))]),
  });
}

/** Min-max scaling intentionally does not clip observations outside the training range. */
export function transform(input, fitted = fit(TRAINING)) {
  if (!input || typeof input.missing !== 'boolean') {
    throw new TypeError('missing must be a boolean.');
  }
  if (!input.missing && (!Number.isFinite(input.area) || input.area < 20 || input.area > 180)) {
    throw new RangeError('Observed area must be between 20 and 180 square metres.');
  }
  if (!Number.isInteger(input.rooms) || input.rooms < 1 || input.rooms > 5) {
    throw new RangeError('Rooms must be a positive integer between 1 and 5.');
  }
  if (!fitted.categories.includes(input.district)) {
    throw new RangeError(`Unknown district: ${input.district}`);
  }
  const filledArea = input.missing ? fitted.median : input.area;
  const scaledArea = (filledArea - fitted.min) / (fitted.max - fitted.min);
  const areaPerRoom = filledArea / input.rooms;
  const missingFlag = Number(input.missing);
  const oneHot = fitted.categories.map(category => Number(input.district === category));
  const vector = [scaledArea, input.rooms, areaPerRoom, missingFlag, ...oneHot];
  const names = ['面积缩放', '房间数', '每室面积', '面积缺失', ...fitted.categories.map(category => `区域·${category}`)];
  return { filledArea, scaledArea, oneHot, areaPerRoom, missingFlag, vector, names };
}
