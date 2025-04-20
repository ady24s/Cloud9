import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css'; // or your preferred CSS file like style.css
import App from './App';
import 'bootstrap/dist/css/bootstrap.min.css'; // Bootstrap import should also be at the top

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);