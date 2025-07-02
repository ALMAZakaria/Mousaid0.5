import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import AIAgent from './components/AIAgent'; // or wherever your home component is
// import other pages

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<AIAgent />} />
        {/* Add other routes here */}
      </Routes>
    </Router>
  );
}

export default App;