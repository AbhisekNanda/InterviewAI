import React, { useState, useEffect, useRef } from 'react';

// --- Helper Components for UI ---
const Card = ({ children, className = '' }) => <div className={`bg-gray-800/80 backdrop-blur-sm border border-gray-700 rounded-2xl shadow-2xl p-8 w-full max-w-4xl mx-auto ${className}`}>{children}</div>;
const Button = ({ children, onClick, disabled = false, className = '' }) => <button onClick={onClick} disabled={disabled} className={`px-8 py-3 font-bold text-white rounded-full transition-all duration-300 focus:outline-none focus:ring-4 focus:ring-indigo-400 disabled:bg-gray-600 ${className}`}>{children}</button>;

// --- Main Page Components ---

const LandingPage = ({ onStart }) => (
  <div className="min-h-screen w-full flex flex-col items-center justify-center text-white text-center p-4" style={{ backgroundImage: `linear-gradient(rgba(17, 24, 39, 0.8), rgba(17, 24, 39, 1)), url('https://placehold.co/1920x1080/0a0a2a/FFFFFF?text=AI+Network')` }}>
    <h1 className="text-5xl md:text-7xl font-extrabold mb-4">Welcome to InterviewAI</h1>
    <p className="text-lg md:text-xl text-gray-300 max-w-2xl mb-8">Practice for your next technical interview with Akshay, our advanced AI agent.</p>
    <Button onClick={onStart} className="bg-indigo-600 hover:bg-indigo-500">Try Now</Button>
  </div>
);

const UploadPage = ({ onUploadSuccess }) => {
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData(e.target);
    if (!formData.get('file').name) {
      setMessage('Please select a resume file.');
      return;
    }
    setIsLoading(true);
    setMessage('Uploading...');
    try {
      const response = await fetch('/pdf/upload_pdf', { method: 'POST', body: formData });
      const result = await response.json();
      if (!response.ok) throw new Error(result.detail || 'Upload failed.');
      setMessage(`Success! Starting session...`);
      setTimeout(() => onUploadSuccess(result.interview_id), 1500);
    } catch (error) {
      setMessage(`Error: ${error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-gray-900">
      <Card>
        <h1 className="text-3xl font-bold text-center text-white mb-2">Interview Setup</h1>
        <p className="text-center text-gray-400 mb-8">Provide your resume and the job details to begin.</p>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="company_info" className="block text-sm font-medium text-gray-300 mb-1 text-left">Company Info</label>
            <textarea id="company_info" name="company_info" className="w-full bg-gray-700 border border-gray-600 rounded-lg p-3 text-white" placeholder="e.g., A leading tech company..."></textarea>
          </div>
          <div>
            <label htmlFor="job_description" className="block text-sm font-medium text-gray-300 mb-1 text-left">Job Description</label>
            <textarea id="job_description" name="job_description" className="w-full bg-gray-700 border border-gray-600 rounded-lg p-3 text-white" placeholder="e.g., Seeking a Python developer..."></textarea>
          </div>
          <div>
            <label htmlFor="resume_file" className="block text-sm font-medium text-gray-300 mb-1 text-left">Resume (PDF)</label>
            <input type="file" id="resume_file" name="file" accept=".pdf" className="w-full text-gray-300 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:bg-indigo-50 file:text-indigo-700"/>
          </div>
          <Button type="submit" disabled={isLoading} className="w-full bg-indigo-600 hover:bg-indigo-500">{isLoading ? 'Processing...' : 'Upload and Start Interview'}</Button>
        </form>
        {message && <div className="mt-6 p-3 rounded-lg text-center font-semibold">{message}</div>}
      </Card>
    </div>
  );
};

const InterviewPage = ({ interviewId, onInterviewComplete }) => {
  const [status, setStatus] = useState('Connecting...');
  const [transcript, setTranscript] = useState('...');
  const [isRecording, setIsRecording] = useState(false);
  const recognitionRef = useRef(null);
  const websocketRef = useRef(null);

  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = true;
    recognitionRef.current = recognition;

    recognition.onstart = () => setIsRecording(true);
    recognition.onend = () => setIsRecording(false);
    recognition.onresult = (event) => {
      let finalTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; ++i) {
        if (event.results[i].isFinal) finalTranscript += event.results[i][0].transcript;
      }
      if (finalTranscript && websocketRef.current) {
        setTranscript(`You said: "${finalTranscript}"`);
        websocketRef.current.send(finalTranscript.trim());
      }
    };

    const wsUrl = `ws://${window.location.host}/ws/interview/${interviewId}`;
    websocketRef.current = new WebSocket(wsUrl);

    websocketRef.current.onopen = () => setStatus("Connected. Waiting for interviewer...");
    websocketRef.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'ai_response') {
        speak(data.text);
      } else if (data.type === 'final_report') {
        onInterviewComplete(data.data);
      }
    };
    websocketRef.current.onerror = () => setStatus("Connection Error.");

    return () => {
      if (websocketRef.current) websocketRef.current.close();
    };
  }, [interviewId, onInterviewComplete]);

  const speak = (text) => {
    const synth = window.speechSynthesis;
    if (synth.speaking) synth.cancel();
    const utterance = new SpeechSynthesisUtterance(text);
    setStatus("Interviewer is speaking...");
    utterance.onend = () => setStatus("Your turn to speak.");
    synth.speak(utterance);
  };

  const toggleRecording = () => {
    if (isRecording) recognitionRef.current.stop();
    else recognitionRef.current.start();
  };

  return (
    <div className="min-h-screen w-full flex items-center justify-center p-4 bg-gray-900">
      <Card className="text-center">
        <h1 className="text-3xl font-bold text-white mb-4">Interview Session #{interviewId}</h1>
        <p className="text-lg text-gray-300 mb-4 h-12 italic">{transcript}</p>
        <p className="text-lg text-yellow-400 mb-8 h-6">{status}</p>
        <button onClick={toggleRecording} className={`relative w-24 h-24 rounded-full flex items-center justify-center mx-auto transition-colors ${isRecording ? 'bg-red-600 animate-pulse' : 'bg-indigo-600'}`}>
          <svg className="w-8 h-8 text-white" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 017 8a1 1 0 10-2 0 7.001 7.001 0 006 6.93V17H9a1 1 0 100 2h6a1 1 0 100-2h-2v-2.07z" clipRule="evenodd"></path>
          </svg>
        </button>
      </Card>
    </div>
  );
};

const ScorePage = ({ report, onRestart }) => (
  <div className="min-h-screen w-full flex items-center justify-center p-4 bg-gray-900">
    <Card className="text-left">
      <h1 className="text-3xl font-bold text-center text-white mb-6">Interview Report</h1>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 text-center">
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-400">Final Score</p>
          <p className="text-3xl font-bold text-green-400">{report.final_score}/100</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-400">Questions Asked</p>
          <p className="text-3xl font-bold text-white">{report.total_questions_asked}</p>
        </div>
        <div className="bg-gray-700 p-4 rounded-lg">
          <p className="text-sm text-gray-400">Correct Answers</p>
          <p className="text-3xl font-bold text-white">{report.total_correct_answers}</p>
        </div>
      </div>
      <div className="space-y-4">
        <div>
          <h3 className="font-bold text-lg text-white">Overall Summary</h3>
          <p className="text-gray-300">{report.overall_summary}</p>
        </div>
        <div>
          <h3 className="font-bold text-lg text-white">Suitability for Role</h3>
          <p className="text-gray-300">{report.suitability_for_role}</p>
        </div>
        <div>
          <h3 className="font-bold text-lg text-white">Points for Improvement</h3>
          <ul className="list-disc list-inside text-gray-300 space-y-1">
            {report.points_for_improvement.map((point, index) => <li key={index}>{point}</li>)}
          </ul>
        </div>
      </div>
      <div className="text-center mt-8">
        <Button onClick={onRestart} className="bg-indigo-600 hover:bg-indigo-500">Try Another Interview</Button>
      </div>
    </Card>
  </div>
);

// --- Main App Component ---
export default function App() {
  const [page, setPage] = useState('landing');
  const [interviewId, setInterviewId] = useState(null);
  const [finalReport, setFinalReport] = useState(null);

  const handleStart = () => setPage('upload');
  const handleUploadSuccess = (id) => { setInterviewId(id); setPage('interview'); };
  const handleInterviewComplete = (report) => { setFinalReport(report); setPage('score'); };
  const handleRestart = () => { setPage('landing'); setInterviewId(null); setFinalReport(null); };

  const renderPage = () => {
    switch (page) {
      case 'upload': return <UploadPage onUploadSuccess={handleUploadSuccess} />;
      case 'interview': return <InterviewPage interviewId={interviewId} onInterviewComplete={handleInterviewComplete} />;
      case 'score': return <ScorePage report={finalReport} onRestart={handleRestart} />;
      default: return <LandingPage onStart={handleStart} />;
    }
  };

  return <div className="bg-gray-900">{renderPage()}</div>;
}
