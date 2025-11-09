import React from 'react';
import './minimalist-theme.css';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import ChatWithBot from './pages/ChatWithBot';
import ArchiveUpload from './pages/ArchiveUpload';
import Notifications from './pages/Notifications';

const App: React.FC = () => (
  <Router>
    <nav style={{ display: 'flex', gap: 20 }}>
      <Link to="/chat">Chat with Bot</Link>
      {/* <Link to="/archive-upload">Archive Upload</Link> */}
      <Link to="/notifications">Notifications</Link>
    </nav>
    <div className="center-wrapper">
      <Routes>
  <Route path="/" element={<ChatWithBot />} />
        <Route path="/chat" element={<ChatWithBot />} />
        {/* <Route path="/archive-upload" element={<ArchiveUpload />} /> */}
        <Route path="/notifications" element={<Notifications />} />
  {/* Removed FAQ and Predictive Accounting pages per requested cleanup */}
      </Routes>
    </div>
  </Router>
);

export default App;

