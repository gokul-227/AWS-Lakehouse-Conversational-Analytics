import React, { createContext, useContext, useState, useEffect } from 'react';
import { Amplify } from 'aws-amplify';
import { signIn, signOut, signUp, confirmSignUp, fetchAuthSession, getCurrentUser } from 'aws-amplify/auth';

Amplify.configure({
  Auth: {
    Cognito: {
      userPoolId: import.meta.env.VITE_COGNITO_USER_POOL_ID,
      userPoolClientId: import.meta.env.VITE_COGNITO_CLIENT_ID,
    }
  }
});

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkUser();
  }, []);

  const checkUser = async () => {
    try {
      const currentUser = await getCurrentUser();
      setUser(currentUser);
    } catch (err) {
      setUser(null);
    } finally {
      setLoading(false);
    }
  };

  const login = async (username, password) => {
    const { isSignedIn } = await signIn({ username, password });
    if (isSignedIn) await checkUser();
  };

  const logout = async () => {
    await signOut();
    setUser(null);
  };

  const register = async (email, password) => {
    return await signUp({
      username: email,
      password,
      options: { userAttributes: { email } }
    });
  };

  const confirmRegistration = async (email, code) => {
    return await confirmSignUp({ username: email, confirmationCode: code });
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, register, confirmRegistration }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
