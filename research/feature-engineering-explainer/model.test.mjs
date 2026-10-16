import test from 'node:test';
import assert from 'node:assert/strict';
import { TRAINING, fit, transform } from './model.mjs';

const sample = { area: 80, rooms: 2, district: '中心', missing: false };

test('training statistics are computed from complete rows and frozen', () => {
  const fitted = fit(TRAINING);
  assert.deepEqual(fitted, { median: 80, min: 40, max: 120, categories: ['中心', '近郊', '远郊'] });
  assert.ok(Object.isFrozen(fitted));
  assert.ok(Object.isFrozen(fitted.categories));
  assert.ok(Object.isFrozen(TRAINING[0]));
  assert.equal(fit(TRAINING.slice(0, 4)).median, 70);
});

test('training endpoints map to zero and one; new values are not clipped', () => {
  for (const [area, expected] of [[40, 0], [120, 1], [180, 1.75], [20, -0.25]]) {
    assert.equal(transform({ ...sample, area }).scaledArea, expected);
  }
});

test('missing area uses the training median and retains missingness', () => {
  const result = transform({ ...sample, area: null, missing: true });
  assert.equal(result.filledArea, 80);
  assert.equal(result.scaledArea, 0.5);
  assert.equal(result.areaPerRoom, 40);
  assert.equal(result.missingFlag, 1);
  assert.equal(transform(sample).missingFlag, 0);
});

test('one-hot values are exclusive, ordered and aligned with the feature vector', () => {
  for (const [index, district] of ['中心', '近郊', '远郊'].entries()) {
    const result = transform({ ...sample, district });
    assert.equal(result.oneHot.reduce((a, b) => a + b, 0), 1);
    assert.equal(result.oneHot[index], 1);
    assert.deepEqual(result.vector, [0.5, 2, 40, 0, ...result.oneHot]);
    assert.equal(result.names.length, result.vector.length);
    assert.equal(result.names[index + 4], `区域·${district}`);
  }
});

test('derived area per room uses the current observed or imputed area', () => {
  assert.equal(transform({ ...sample, area: 120, rooms: 3 }).areaPerRoom, 40);
  assert.equal(transform({ ...sample, rooms: 5, missing: true }).areaPerRoom, 16);
});

test('invalid observations and unseen categories fail explicitly', () => {
  for (const area of [19, 181, NaN, Infinity, '80', null]) {
    assert.throws(() => transform({ ...sample, area }), /area/);
  }
  for (const rooms of [0, -1, 1.5, 6, NaN]) {
    assert.throws(() => transform({ ...sample, rooms }), /Rooms/);
  }
  assert.throws(() => transform({ ...sample, district: '未知' }), /Unknown district/);
  assert.throws(() => transform({ ...sample, missing: 1 }), /boolean/);
});

test('invalid training data and zero-range scaler fail explicitly', () => {
  assert.throws(() => fit([]), /two complete rows/);
  assert.throws(() => fit([TRAINING[0], { ...TRAINING[1], area: NaN }]), /Training rows/);
  assert.throws(() => fit([TRAINING[0], TRAINING[0]]), /nonzero training range/);
});

test('new inputs cannot leak into fitted statistics or subsequent transforms', () => {
  const fitted = fit(TRAINING);
  const before = JSON.stringify(fitted);
  const original = transform(sample, fitted);
  transform({ ...sample, area: 180, district: '远郊' }, fitted);
  transform({ ...sample, area: 20, missing: true }, fitted);
  assert.equal(JSON.stringify(fitted), before);
  assert.deepEqual(transform(sample, fitted), original);
  assert.throws(() => { fitted.max = 180; }, TypeError);
  assert.throws(() => fitted.categories.push('未知'), TypeError);
});
