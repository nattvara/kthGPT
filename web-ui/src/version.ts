export const buildDate = 'BUILD_DATE';

export let isProduction: boolean;

if (process.env.NODE_ENV === 'production') {
  isProduction = true;
} else {
  isProduction = false;
}
