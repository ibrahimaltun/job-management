import React, { useState } from 'react';
import { TextField, Button, Paper, Typography, Box, Link } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import axios from 'axios';

const SignIn = ({ onLoginSuccess }) => {
    const [form, setForm] = useState({ username: '', password: '' });
    const navigate = useNavigate();

    const handleLogin = async () => {
        try {
            const res = await axios.post('http://127.0.0.1:5000/login', form);
            localStorage.setItem('token', res.data.token);
            localStorage.setItem('role', res.data.role);
            localStorage.setItem('username', res.data.username); // <--- İsmi sakla

            onLoginSuccess();
            navigate('/dashboard');
        } catch (err) {
            alert("Giriş başarısız!");
        }
    };

    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
            <Paper sx={{ p: 4, width: 350 }}>
                <Typography variant="h5" mb={2}>Giriş Yap</Typography>
                <TextField fullWidth label="Kullanıcı Adı" margin="normal" onChange={(e) => setForm({ ...form, username: e.target.value })} />
                <TextField fullWidth label="Şifre" type="password" margin="normal" onChange={(e) => setForm({ ...form, password: e.target.value })} />
                <Button fullWidth variant="contained" sx={{ mt: 2 }} onClick={handleLogin}>Giriş</Button>

                <Box mt={2} textAlign="center">
                    <Typography variant="body2">
                        Kayıtlı değil misiniz? <Link component={RouterLink} to="/signup">Üye Ol</Link>
                    </Typography>
                </Box>
            </Paper>
        </Box>
    );
};

export default SignIn;

