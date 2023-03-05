import axios from 'axios';

export interface ServerResponse {
  data: object | object[];
  headers: object;
  status: number;
  statusText: string;
}

export interface ServerErrorResponse {
  response: {
    data: {
      detail: string;
    };
    headers: object;
    status: number;
    statusText: string;
  };
  code: string;
}

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
