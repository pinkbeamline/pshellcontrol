import ch.psi.pshell.ui.Panel;
import ch.psi.utils.State;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 *
 */
public class pp1 extends Panel {

    public pp1() {
        initComponents();
    }

    //Overridable callbacks
    @Override
    public void onInitialize(int runCount) {

    }

    @Override
    public void onStateChange(State state, State former) {

    }

    @Override
    public void onExecutedFile(String fileName, Object result) {
    }

    
    //Callback to perform update - in event thread
    @Override
    protected void doUpdate() {
    }

    @SuppressWarnings("unchecked")
    // <editor-fold defaultstate="collapsed" desc="Generated Code">//GEN-BEGIN:initComponents
    private void initComponents() {

        buttonRun = new javax.swing.JButton();
        jLabel1 = new javax.swing.JLabel();
        jSpinner1 = new javax.swing.JSpinner();
        txtout1 = new javax.swing.JTextField();
        buttonRun1 = new javax.swing.JButton();
        buttonRun2 = new javax.swing.JButton();

        buttonRun.setText("Run");
        buttonRun.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                buttonRunActionPerformed(evt);
            }
        });

        jLabel1.setText("X:");

        jSpinner1.setModel(new javax.swing.SpinnerNumberModel(0.0d, null, null, 0.01d));

        txtout1.setText("0");
        txtout1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                txtout1ActionPerformed(evt);
            }
        });

        buttonRun1.setText("Run");
        buttonRun1.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                buttonRun1ActionPerformed(evt);
            }
        });

        buttonRun2.setText("Run");
        buttonRun2.addActionListener(new java.awt.event.ActionListener() {
            public void actionPerformed(java.awt.event.ActionEvent evt) {
                buttonRun2ActionPerformed(evt);
            }
        });

        javax.swing.GroupLayout layout = new javax.swing.GroupLayout(this);
        this.setLayout(layout);
        layout.setHorizontalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
                    .addGroup(layout.createSequentialGroup()
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(buttonRun, javax.swing.GroupLayout.PREFERRED_SIZE, 95, javax.swing.GroupLayout.PREFERRED_SIZE)
                            .addGroup(layout.createSequentialGroup()
                                .addComponent(jLabel1)
                                .addPreferredGap(javax.swing.LayoutStyle.ComponentPlacement.RELATED)
                                .addComponent(jSpinner1)))
                        .addGap(43, 43, 43)
                        .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING, false)
                            .addComponent(buttonRun1, javax.swing.GroupLayout.DEFAULT_SIZE, 95, Short.MAX_VALUE)
                            .addComponent(txtout1)))
                    .addComponent(buttonRun2, javax.swing.GroupLayout.PREFERRED_SIZE, 95, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addContainerGap(203, Short.MAX_VALUE))
        );
        layout.setVerticalGroup(
            layout.createParallelGroup(javax.swing.GroupLayout.Alignment.LEADING)
            .addGroup(javax.swing.GroupLayout.Alignment.TRAILING, layout.createSequentialGroup()
                .addContainerGap()
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(jLabel1)
                    .addComponent(jSpinner1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE)
                    .addComponent(txtout1, javax.swing.GroupLayout.PREFERRED_SIZE, javax.swing.GroupLayout.DEFAULT_SIZE, javax.swing.GroupLayout.PREFERRED_SIZE))
                .addGap(18, 18, 18)
                .addGroup(layout.createParallelGroup(javax.swing.GroupLayout.Alignment.BASELINE)
                    .addComponent(buttonRun)
                    .addComponent(buttonRun1))
                .addGap(18, 18, 18)
                .addComponent(buttonRun2)
                .addContainerGap(19, Short.MAX_VALUE))
        );
    }// </editor-fold>//GEN-END:initComponents

    private void buttonRunActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_buttonRunActionPerformed
        try{
            txtout1.setText(jSpinner1.getValue().toString());
            Map args = new HashMap();
            args.put("myx", jSpinner1.getValue());
            this.runAsync("pp1", args, false).handle((ret, ex)->{
                if(ex != null){
                    if (!getContext().isAborted()){
                        showException((Exception) ex);
                    }
                } else {
                    if (ret instanceof List){
                        txtout1.setText("Error: 1");
                    }
                    showMessage("Status", "Success");
                }
                return ret;
            });
            
        } catch (Exception ex) {
            showException(ex);
        }
    }//GEN-LAST:event_buttonRunActionPerformed

    private void buttonRun1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_buttonRun1ActionPerformed
        try{
            txtout1.setText(jSpinner1.getValue().toString());
            Map args = new HashMap();
            args.put("myx", jSpinner1.getValue());
            this.runAsync("pp1", args, false);
        } catch (Exception ex) {
            showException(ex);
        }
    }//GEN-LAST:event_buttonRun1ActionPerformed

    private void txtout1ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_txtout1ActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_txtout1ActionPerformed

    private void buttonRun2ActionPerformed(java.awt.event.ActionEvent evt) {//GEN-FIRST:event_buttonRun2ActionPerformed
        // TODO add your handling code here:
    }//GEN-LAST:event_buttonRun2ActionPerformed

    // Variables declaration - do not modify//GEN-BEGIN:variables
    private javax.swing.JButton buttonRun;
    private javax.swing.JButton buttonRun1;
    private javax.swing.JButton buttonRun2;
    private javax.swing.JLabel jLabel1;
    private javax.swing.JSpinner jSpinner1;
    private javax.swing.JTextField txtout1;
    // End of variables declaration//GEN-END:variables
}
