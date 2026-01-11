
// Scraps lol. figure out later

const allowedSet = new Set(
  groupKeys.flatMap(key => unitGroups[key])
);

const currentUnit = unitSelect.value;

unitTypes.forEach(option => {
  option.hidden = !allowedSet.has(option.value);
});

if (!allowedSet.has(currentUnit)) {
  unitSelect.value = '';
}
