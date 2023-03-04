import axios from 'axios';

let baseURL: string;

if (process.env.NODE_ENV === 'production') {
  baseURL = '/api';
} else {
  baseURL = 'http://localhost:8000';
}

export const makeUrl = (uri: string) => `${baseURL}${uri}`;

export default axios.create({
  baseURL,
  headers: {
    'Content-type': 'application/json',
  },
});
