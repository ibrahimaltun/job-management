import React, { useEffect, useState } from 'react';
import { TextField, Button, Paper, Typography, Box, ToggleButton, ToggleButtonGroup, Link, Snackbar, Alert } from '@mui/material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import axios from 'axios';

const SignUp = () => {
    const [form, setForm] = useState({ username: '', password: '', role: 'worker' });
    const [notification, setNotification] = useState({ open: false, message: '', severity: 'info' });
    const navigate = useNavigate();

    const handleClose = () => setNotification({ ...notification, open: false });

    const handleRegister = async () => {
        // Client-side quick check
        const trimmedUsername = form.username.trim();

        // 2. Front-end Validation Logic
        if (!trimmedUsername || !form.password) {
            setNotification({
                open: true,
                message: "Kullanıcı adı ve şifre boş bırakılamaz!",
                severity: 'error'
            });
            return; // Stop the function here
        }

        if (form.password.length < 5) {
            setNotification({
                open: true,
                message: "Şifre en az 5 karakter olmalıdır!",
                severity: 'warning'
            });
            return;
        }

        try {
            const res = await axios.post('http://localhost:5000/register', form);
            setNotification({ open: true, message: res.data.msg, severity: 'success' });
            // Redirect after a short delay to let user see the success message
            setTimeout(() => navigate('/signin'), 2000);
        } catch (err) {
            const errorMsg = err.response?.data?.msg || "Kayıt sırasında bir hata oluştu!";
            setNotification({ open: true, message: errorMsg, severity: 'error' });
        }
    };

    return (
        <Box sx={{ display: 'flex', justifyContent: 'center', mt: 10 }}>
            <Paper sx={{ p: 4, width: 350 }}>
                <Typography variant="h5" mb={2}>Üye Ol</Typography>
                <TextField fullWidth label="Kullanıcı Adı"
                    margin="normal"
                    error={form.username === ""} // Visual red border if empty
                    helperText={form.username === "" ? "Bu alan zorunludur" : ""}
                    onChange={(e) => setForm({ ...form, username: e.target.value })} />
                <TextField fullWidth label="Şifre" type="password"
                    margin="normal"
                    error={form.password.length > 0 && form.password.length < 5}
                    helperText={form.password.length > 0 && form.password.length < 5 ? "Minimum 5 karakter" : ""}
                    onChange={(e) => setForm({ ...form, password: e.target.value })} />

                <Typography variant="caption" display="block" mt={2}>Hesap Türü:</Typography>
                <ToggleButtonGroup
                    exclusive value={form.role}
                    onChange={(e, val) => val && setForm({ ...form, role: val })}
                    fullWidth sx={{ mb: 2 }}
                >
                    <ToggleButton value="worker">Çalışan</ToggleButton>
                    <ToggleButton value="leader">Lider</ToggleButton>
                </ToggleButtonGroup>

                <Button fullWidth variant="contained" onClick={handleRegister}>Kayıt Ol</Button>
                <Box mt={2} textAlign="center">
                    <Link component={RouterLink} to="/signin">Zaten hesabım var</Link>
                </Box>
            </Paper>
            {/* MUI Notification System */}
            <Snackbar open={notification.open} autoHideDuration={4000} onClose={handleClose} anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}>
                <Alert onClose={handleClose} severity={notification.severity} sx={{ width: '100%' }} variant="filled">
                    {notification.message}
                </Alert>
            </Snackbar>
        </Box>
    );
};

export default SignUp;
