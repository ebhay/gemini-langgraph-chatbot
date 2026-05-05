'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '@/lib/store';
import { chatAPI } from '@/lib/api';
import Sidebar from '@/components/Sidebar';
import ChatArea from '@/components/ChatArea';
import ProfileModal from '@/components/ProfileModal';

export default function ChatPage() {
  const router = useRouter();
  const { user, setUser, setSessions, setCurrentSessionId, setMessages, setNotifications, setProfile } = useStore();
  const [showProfile, setShowProfile] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    const userStr = localStorage.getItem('user');

    if (!token || !userStr) {
      router.push('/login');
      return;
    }

    setUser(JSON.parse(userStr));
    loadData();

    const notifInterval = setInterval(() => {
      loadNotifications();
    }, 10000);

    return () => clearInterval(notifInterval);
  }, []);

  const loadData = async () => {
    try {
      const [sessionsRes, profileRes, notifsRes] = await Promise.all([
        chatAPI.getSessions(),
        chatAPI.getProfile(),
        chatAPI.getNotifications(),
      ]);

      setSessions(sessionsRes.data);
      setProfile(profileRes.data);
      setNotifications(notifsRes.data);

      if (sessionsRes.data.length > 0) {
        const firstSession = sessionsRes.data[0].id;
        setCurrentSessionId(firstSession);
        loadSessionHistory(firstSession);
      }
    } catch (error) {
      console.error('Failed to load data:', error);
    }
  };

  const loadSessionHistory = async (sessionId: string) => {
    try {
      const res = await chatAPI.getSessionHistory(sessionId);
      setMessages(res.data);
    } catch (error) {
      console.error('Failed to load session history:', error);
    }
  };

  const loadNotifications = async () => {
    try {
      const res = await chatAPI.getNotifications();
      setNotifications(res.data);
    } catch (error) {
      console.error('Failed to load notifications:', error);
    }
  };

  if (!user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary"></div>
      </div>
    );
  }

  return (
    <div className="flex h-screen bg-background">
      <Sidebar
        isOpen={sidebarOpen}
        onToggle={() => setSidebarOpen(!sidebarOpen)}
        onProfileClick={() => setShowProfile(true)}
        onSessionChange={loadSessionHistory}
      />
      <ChatArea sidebarOpen={sidebarOpen} onToggleSidebar={() => setSidebarOpen(!sidebarOpen)} />
      {showProfile && <ProfileModal onClose={() => setShowProfile(false)} />}
    </div>
  );
}
