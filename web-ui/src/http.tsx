import axios from 'axios';

const baseURL = 'http://localhost:8000';

export const makeUrl = (uri: string) => `${baseURL}${uri}`;

export default axios.create({
  baseURL,
  headers: {
    'Content-type': 'application/json'
  }
});
