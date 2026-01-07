import { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

export default function Docs() {
  const router = useRouter();
  const { project_id } = router.query;

  const [project, setProject] = useState(null);
  const [documentation, setDocumentation] = useState('');
  const [files, setFiles] = useState([]);
  const [ktPlan, setKtPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('docs');
  const [chatQuestion, setChatQuestion] = useState('');
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);

  useEffect(() => {
    if (project_id) {
      fetchProjectData();
      fetchKTPlan();
    }
  }, [project_id]);

  const fetchProjectData = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/docs/${project_id}`);
      const data = await response.json();

      setProject(data.project);
      setDocumentation(data.documentation);
      setFiles(data.files);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching project data:', error);
      setLoading(false);
    }
  };

  const fetchKTPlan = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/kt/${project_id}`);
      const data = await response.json();
      setKtPlan(data.kt_plan);
    } catch (error) {
      console.error('Error fetching KT plan:', error);
    }
  };

  const handleChat = async (e) => {
    e.preventDefault();
    if (!chatQuestion.trim()) return;

    const question = chatQuestion;
    setChatQuestion('');
    setChatLoading(true);

    // Add user question to chat
    setChatHistory([...chatHistory, { type: 'question', text: question }]);

    try {
      const response = await fetch('http://localhost:8000/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, project_id })
      });

      const data = await response.json();

      setChatHistory([
        ...chatHistory,
        { type: 'question', text: question },
        { type: 'answer', text: data.answer, sources: data.sources }
      ]);
    } catch (error) {
      console.error('Chat error:', error);
      setChatHistory([
        ...chatHistory,
        { type: 'question', text: question },
        { type: 'error', text: 'Failed to get answer' }
      ]);
    } finally {
      setChatLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading documentation...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">Project Documentation</h1>
          {project && (
            <p className="text-sm text-gray-600 mt-1">
              {project.path} • {project.role} • {project.files_analyzed} files analyzed
            </p>
          )}
        </div>
      </div>

      {/* Tabs */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4">
          <nav className="flex space-x-8">
            <button
              onClick={() => setActiveTab('docs')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'docs'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Documentation
            </button>
            <button
              onClick={() => setActiveTab('kt')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'kt'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              KT Plan
            </button>
            <button
              onClick={() => setActiveTab('chat')}
              className={`py-4 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'chat'
                  ? 'border-indigo-500 text-indigo-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              Ask Questions
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'docs' && (
          <div className="bg-white rounded-lg shadow p-8">
            <div className="prose max-w-none">
              <div className="whitespace-pre-wrap">{documentation}</div>
            </div>

            {files && files.length > 0 && (
              <div className="mt-8 pt-8 border-t border-gray-200">
                <h3 className="text-lg font-semibold mb-4">Analyzed Files ({files.length})</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {files.map((file, idx) => (
                    <div key={idx} className="p-4 bg-gray-50 rounded-lg">
                      <p className="font-mono text-sm text-gray-900">{file.file_name}</p>
                      <p className="text-xs text-gray-500 mt-1">
                        Complexity: {file.complexity} •
                        {file.classes && ` ${file.classes.length} classes`} •
                        {file.functions && ` ${file.functions.length} functions`}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {activeTab === 'kt' && ktPlan && (
          <div className="bg-white rounded-lg shadow p-8">
            <h2 className="text-2xl font-bold mb-6">10-Day Knowledge Transfer Plan</h2>
            {ktPlan.plan && ktPlan.plan.map((day) => (
              <div key={day.day} className="mb-8 pb-8 border-b border-gray-200 last:border-0">
                <div className="flex items-start">
                  <div className="flex-shrink-0 w-12 h-12 bg-indigo-100 rounded-full flex items-center justify-center">
                    <span className="text-indigo-600 font-bold">{day.day}</span>
                  </div>
                  <div className="ml-4 flex-1">
                    <h3 className="text-lg font-semibold text-gray-900">{day.title}</h3>
                    <p className="text-gray-600 mt-2">{day.focus}</p>

                    {day.files_to_study && day.files_to_study.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-900">Files to Study:</h4>
                        <ul className="list-disc list-inside text-gray-600 mt-1">
                          {day.files_to_study.map((file, idx) => (
                            <li key={idx} className="font-mono text-sm">{file}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {day.concepts && day.concepts.length > 0 && (
                      <div className="mt-4">
                        <h4 className="font-medium text-gray-900">Key Concepts:</h4>
                        <ul className="list-disc list-inside text-gray-600 mt-1">
                          {day.concepts.map((concept, idx) => (
                            <li key={idx}>{concept}</li>
                          ))}
                        </ul>
                      </div>
                    )}

                    {day.exercise && (
                      <div className="mt-4 p-4 bg-blue-50 rounded-lg">
                        <h4 className="font-medium text-gray-900">Exercise:</h4>
                        <p className="text-gray-700 mt-1">{day.exercise}</p>
                      </div>
                    )}

                    {day.checkpoint_questions && day.checkpoint_questions.length > 0 && (
                      <div className="mt-4 p-4 bg-green-50 rounded-lg">
                        <h4 className="font-medium text-gray-900">Knowledge Checkpoints:</h4>
                        <ul className="list-decimal list-inside text-gray-700 mt-1">
                          {day.checkpoint_questions.map((question, idx) => (
                            <li key={idx}>{question}</li>
                          ))}
                        </ul>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {activeTab === 'chat' && (
          <div className="bg-white rounded-lg shadow">
            <div className="p-6 border-b border-gray-200">
              <h2 className="text-xl font-semibold">Ask Questions About the Codebase</h2>
              <p className="text-gray-600 text-sm mt-1">Get instant answers powered by AI</p>
            </div>

            <div className="h-96 overflow-y-auto p-6 space-y-4">
              {chatHistory.length === 0 ? (
                <div className="text-center text-gray-500 mt-12">
                  <p>Ask any question about the codebase to get started!</p>
                </div>
              ) : (
                chatHistory.map((msg, idx) => (
                  <div key={idx} className={`${msg.type === 'question' ? 'text-right' : 'text-left'}`}>
                    <div className={`inline-block max-w-3xl rounded-lg px-4 py-2 ${
                      msg.type === 'question'
                        ? 'bg-indigo-600 text-white'
                        : msg.type === 'error'
                        ? 'bg-red-100 text-red-800'
                        : 'bg-gray-100 text-gray-900'
                    }`}>
                      <p className="whitespace-pre-wrap">{msg.text}</p>
                      {msg.sources && (
                        <div className="mt-2 pt-2 border-t border-gray-300 text-xs">
                          <p className="font-semibold">Sources:</p>
                          {msg.sources.map((source, i) => (
                            <p key={i} className="font-mono">{source.file_name}</p>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              )}
              {chatLoading && (
                <div className="text-left">
                  <div className="inline-block bg-gray-100 rounded-lg px-4 py-2">
                    <div className="flex items-center space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-100"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce delay-200"></div>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <form onSubmit={handleChat} className="p-6 border-t border-gray-200">
              <div className="flex space-x-4">
                <input
                  type="text"
                  value={chatQuestion}
                  onChange={(e) => setChatQuestion(e.target.value)}
                  placeholder="Ask a question about the codebase..."
                  className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  disabled={chatLoading}
                />
                <button
                  type="submit"
                  disabled={chatLoading || !chatQuestion.trim()}
                  className="px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400 transition-colors"
                >
                  Send
                </button>
              </div>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}
