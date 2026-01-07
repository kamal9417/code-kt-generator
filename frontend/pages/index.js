import { useState } from 'react';
import { useRouter } from 'next/router';

export default function Home() {
  const [path, setPath] = useState('');
  const [role, setRole] = useState('fullstack');
  const [loading, setLoading] = useState(false);
  const router = useRouter();

  const handleAnalyze = async () => {
    if (!path) {
      alert('Please enter a project path');
      return;
    }

    setLoading(true);
    
    try {
      const response = await fetch('http://localhost:8000/api/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ path, role })
      });

      const data = await response.json();
      
      if (response.ok) {
        // Redirect to documentation page
        router.push(`/docs?project_id=${data.project_id}`);
      } else {
        alert(data.detail || 'Error analyzing project');
      }
    } catch (error) {
      alert('Failed to connect to server');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 max-w-2xl w-full">
        <h1 className="text-4xl font-bold text-gray-800 mb-2">
          📚 Code Documentation & KT Generator
        </h1>
        <p className="text-gray-600 mb-8">
          Automatically generate documentation and personalized onboarding plans from your codebase
        </p>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Project Folder Path
            </label>
            <input
              type="text"
              value={path}
              onChange={(e) => setPath(e.target.value)}
              placeholder="/home/user/my-project"
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Your Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
            >
              <option value="fullstack">Full Stack Developer</option>
              <option value="frontend">Frontend Developer</option>
              <option value="backend">Backend Developer</option>
              <option value="devops">DevOps Engineer</option>
            </select>
          </div>

          <button
            onClick={handleAnalyze}
            disabled={loading}
            className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
          >
            {loading ? '🔄 Analyzing...' : '🚀 Generate Documentation & KT'}
          </button>
        </div>

        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">✨ What you'll get:</h3>
          <ul className="text-sm text-gray-600 space-y-1">
            <li>✅ Comprehensive project documentation</li>
            <li>✅ Personalized 10-day learning plan</li>
            <li>✅ Interactive codebase Q&A</li>
            <li>✅ Knowledge checkpoints</li>
          </ul>
        </div>
      </div>
    </div>
  );
}