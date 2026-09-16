// Convert naira amounts to words — e.g. 1_250_000 → "One Million, Two Hundred and Fifty Thousand Naira"
const ONES = ['', 'One', 'Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Eleven', 'Twelve', 'Thirteen', 'Fourteen', 'Fifteen', 'Sixteen', 'Seventeen', 'Eighteen', 'Nineteen'];
const TENS = ['', '', 'Twenty', 'Thirty', 'Forty', 'Fifty', 'Sixty', 'Seventy', 'Eighty', 'Ninety'];
const SCALES = ['', 'Thousand', 'Million', 'Billion', 'Trillion'];

function twoDigits(n) {
  if (n < 20) return ONES[n];
  const tens = Math.floor(n / 10);
  const ones = n % 10;
  return `${TENS[tens]}${ones ? `-${ONES[ones]}` : ''}`;
}

function threeDigits(n) {
  const hundreds = Math.floor(n / 100);
  const rest = n % 100;
  let out = '';
  if (hundreds) out += `${ONES[hundreds]} Hundred`;
  if (rest) out += `${out ? ' and ' : ''}${twoDigits(rest)}`;
  return out;
}

export function toWords(amount = 0) {
  let n = Math.round(Math.abs(amount));
  if (n === 0) return { words: 'Zero Naira', minorWords: 'Zero Kobo' };

  const parts = [];
  let scale = 0;
  while (n > 0) {
    const chunk = n % 1000;
    if (chunk) {
      const text = threeDigits(chunk);
      parts.unshift(`${text}${SCALES[scale] ? ` ${SCALES[scale]}` : ''}`);
    }
    n = Math.floor(n / 1000);
    scale += 1;
  }

  const joined = parts.join(', ');
  const kobo = Math.round(Math.abs(amount - Math.trunc(amount)) * 100);
  return {
    words: `${joined} Naira`,
    minorWords: kobo ? `${twoDigits(kobo)} Kobo` : 'Zero Kobo',
  };
}

export default toWords;