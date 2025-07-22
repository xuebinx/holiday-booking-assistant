"use client";
import React, { useEffect, useState } from "react";
import { auth } from "../firebase";
import { GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged, User } from "firebase/auth";

export default function AuthHeader() {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoading(false);
    });
    return () => unsub();
  }, []);

  const handleGoogleSignIn = async () => {
    const provider = new GoogleAuthProvider();
    await signInWithPopup(auth, provider);
  };

  const handleSignOut = async () => {
    await signOut(auth);
  };

  if (loading) return null;

  return (
    <div className="flex items-center gap-4">
      {user ? (
        <>
          {user.photoURL && (
            <img src={user.photoURL} alt="avatar" className="w-8 h-8 rounded-full border" />
          )}
          <span className="font-medium text-gray-800">{user.displayName || user.email}</span>
          <button onClick={handleSignOut} className="text-sm px-3 py-1 bg-gray-200 rounded hover:bg-gray-300">Sign out</button>
        </>
      ) : (
        <>
          <button onClick={handleGoogleSignIn} className="text-sm px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">Sign in with Google</button>
        </>
      )}
    </div>
  );
} 